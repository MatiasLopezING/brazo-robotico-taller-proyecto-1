/*=============================================================================
 * ensayo_barrido.c
 *
 * Ensayo de barrido angular del servomotor MG996R.
 * Grupo 3 - Taller de Proyecto I (E0306) - UNLP - 5-11-2026
 *
 * Mide el recorrido mecanico real entre los dos extremos de consigna, con el
 * servomotor sin carga y sin engranaje montado. Todo el reparto de dientes de
 * la transmision (seccion 4.7 del informe) supone que el MG996R barre 180
 * grados, dato del proveedor, contra los 120 que declara la hoja de datos.
 * Este ensayo resuelve esa diferencia sobre una unidad real.
 *
 * Plataforma:    EDU-CIAA-NXP, biblioteca sAPI v0.6.2.
 * Arquitectura:  superbucle con retardos no bloqueantes y maquina de estados
 *                finitos, igual que el firmware de la seccion 5.1.
 *
 * IMPORTANTE - escala de sAPI. En sapi_servo.c la conversion es
 *
 *     us = SERVO_MINUPTIME_PERIOD + (grados * SERVO_MAXUPTIME_PERIOD) / 180
 *        = 500 + (grados * 2000) / 180
 *
 * de modo que el argumento de servoWrite NO es el angulo del servomotor sino
 * un indice sobre un rango de pulso de 500 a 2500 us:
 *
 *     servoWrite(s,   0)  ->   500 us    fuera del rango nominal
 *     servoWrite(s,  45)  ->  1000 us    extremo nominal del MG996R
 *     servoWrite(s,  90)  ->  1500 us    centro
 *     servoWrite(s, 135)  ->  2000 us    extremo nominal del MG996R
 *     servoWrite(s, 180)  ->  2500 us    fuera del rango nominal
 *
 * Por eso el ensayo arranca en 45 y 135, que es el pulso de 1,0 a 2,0 ms del
 * requerimiento 3.2.2, y se ensancha con TEC2 y TEC3 hasta encontrar el
 * extremo util real. Arrancar en 0 y 180 lleva el servomotor contra su tope
 * interno, con corriente de bloqueo y calentamiento.
 *
 * Prefijos de los mensajes por puerto serie, para poder filtrar el log:
 *   INIT   arranque y configuracion
 *   PASO   instruccion para el operador
 *   DATA   valor a anotar en la planilla
 *   ERROR  falla
 *
 * Conexionado:
 *   senal del servo  -> P1 pin 36  (T_FIL1 = SERVO0)
 *   + del servo      -> +5 V del bus de potencia, NO de la placa
 *   masa del servo   -> negro del bus, unido a la masa de la EDU-CIAA
 *
 * La masa comun no es opcional: el ancho del pulso se mide contra ella.
 *===========================================================================*/

/*==================[inclusiones]============================================*/

#include "sapi.h"
#include <stdio.h>

/*==================[definiciones]===========================================*/

/* Canal bajo ensayo. SERVO0 sale por el pin 36 de P1 (T_FIL1).              */
#define SERVO_ENSAYO           SERVO0

/* Conversion de sapi_servo.c, replicada para poder informar el pulso real.  */
#define PULSO_MINIMO_US        500
#define PULSO_SPAN_US          2000

/* Extremos del ensayo: el rango nominal de 1,0 a 2,0 ms.                    */
#define CONSIGNA_MIN           45
#define CONSIGNA_MAX           135

/* Tope absoluto de la escala. El ajuste fino puede salir del rango nominal
 * para buscar el extremo util, pero nunca de la escala del controlador.     */
#define LIMITE_INFERIOR        0
#define LIMITE_SUPERIOR        180
#define TRIM                   1

/* Rampa de consigna. Un salto es una aceleracion infinita para el
 * servomotor, y ademas enmascara el juego del tren interno.                 */
#define VELOCIDAD_POR_S        60
#define PERIODO_RAMPA_MS       20     /* una trama PWM de 50 Hz              */
#define PASO_RAMPA_DECIMAS     ((VELOCIDAD_POR_S * PERIODO_RAMPA_MS) / 100)

#define ASENTAMIENTO_MS        1500   /* espera tras llegar al extremo       */
#define PERIODO_TECLAS_MS      20     /* muestreo con antirrebote            */
#define REPETICIONES           3

#define UART_BAUDIOS           115200
#define LARGO_MENSAJE          160

/*==================[tipos]==================================================*/

typedef enum {
   ESTADO_MOVIENDO,            /* la consigna avanza hacia el objetivo       */
   ESTADO_ASENTANDO,           /* llego al extremo, se espera a que se quede */
   ESTADO_ESPERANDO_OPERADOR,  /* marcando o midiendo con el transportador   */
   ESTADO_FIN                  /* ensayo terminado, servo en el extremo cero */
} estadoEnsayo_t;

/*==================[variables globales]=====================================*/

static estadoEnsayo_t estado = ESTADO_MOVIENDO;

static int16_t consignaDecimas = CONSIGNA_MIN * 10;
static int16_t objetivoDecimas = CONSIGNA_MIN * 10;

static uint8_t repeticion      = 0;
static bool_t  enExtremoFinal  = FALSE;
static bool_t  finalizando     = FALSE;

static delay_t temporizadorRampa;
static delay_t temporizadorTeclas;
static delay_t temporizadorAsentamiento;

static bool_t previaTec1 = FALSE;
static bool_t previaTec2 = FALSE;
static bool_t previaTec3 = FALSE;
static bool_t previaTec4 = FALSE;

static char mensaje[LARGO_MENSAJE];

/*==================[funciones auxiliares]===================================*/

/**
 * @brief Envia una linea por el puerto serie de depuracion.
 *
 * Escribe sobre UART_USB, que es el puerto micro-USB de aplicacion y
 * depuracion de la placa. A 115200 baudios una linea de LARGO_MENSAJE
 * caracteres ocupa unos 14 ms: no usar dentro de una interrupcion.
 *
 * @param texto Cadena terminada en cero.
 */
static void informar( const char *texto )
{
   uartWriteString( UART_USB, texto );
   uartWriteString( UART_USB, "\r\n" );
}

/**
 * @brief Ancho de pulso que sAPI genera para un valor de consigna.
 *
 * Replica con la misma aritmetica entera la cuenta de valueToMicroseconds,
 * de modo que el valor informado sea el que realmente sale por el pin.
 *
 * @param valor Consigna entera, de 0 a 180.
 * @return Ancho del pulso en microsegundos.
 */
static uint32_t pulsoEnMicrosegundos( uint8_t valor )
{
   return PULSO_MINIMO_US + ( (uint32_t)valor * PULSO_SPAN_US ) / 180;
}

/**
 * @brief Acota la consigna a la escala del controlador y la escribe.
 *
 * La consigna se acota en el firmware y no se confia en que el operador no
 * pase los limites con las teclas de ajuste fino.
 *
 * @return TRUE si el servomotor acepto el valor.
 */
static bool_t aplicarConsigna( void )
{
   if( consignaDecimas < LIMITE_INFERIOR * 10 ) {
      consignaDecimas = LIMITE_INFERIOR * 10;
   }
   if( consignaDecimas > LIMITE_SUPERIOR * 10 ) {
      consignaDecimas = LIMITE_SUPERIOR * 10;
   }

   if( servoWrite( SERVO_ENSAYO, (uint16_t)( consignaDecimas / 10 ) ) == FALSE ) {
      informar( "ERROR: servoWrite rechazo la consigna" );
      return FALSE;
   }
   return TRUE;
}

/**
 * @brief Detecta el flanco de pulsacion de una tecla de la placa.
 *
 * Las teclas TEC1 a TEC4 son activas por nivel bajo. El antirrebote es por
 * muestreo: esta funcion se llama una vez cada PERIODO_TECLAS_MS.
 *
 * @param tecla    Identificador de la tecla.
 * @param anterior Estado leido en el muestreo previo; se actualiza.
 * @return TRUE una sola vez por pulsacion.
 */
static bool_t flancoDeTecla( gpioMap_t tecla, bool_t *anterior )
{
   bool_t ahora  = ( gpioRead( tecla ) == FALSE );
   bool_t flanco = ( ahora == TRUE ) && ( *anterior == FALSE );
   *anterior = ahora;
   return flanco;
}

/**
 * @brief Informa consigna, pulso e instruccion que toca al operador.
 */
static void informarPaso( void )
{
   uint8_t valor = (uint8_t)( consignaDecimas / 10 );

   snprintf( mensaje, sizeof( mensaje ),
             "DATA: repeticion=%d extremo=%s consigna=%d pulso=%lu us",
             (int)( repeticion + 1 ),
             ( enExtremoFinal == TRUE ) ? "final" : "inicial",
             (int)valor,
             (unsigned long)pulsoEnMicrosegundos( valor ) );
   informar( mensaje );

   if( enExtremoFinal == FALSE ) {
      informar( "PASO: marcar con corrector una linea sobre la estrella y "
                "otra enfrentada sobre la carcasa. TEC1 para continuar" );
   } else {
      informar( "PASO: medir con transportador el angulo entre las dos marcas "
                "y anotarlo. TEC1 para continuar" );
   }
   informar( "PASO: si el motor zumba con el eje quieto esta forzando contra "
             "su tope interno: acercar el extremo con TEC2 o TEC3" );
}

/**
 * @brief Corre la secuencia del ensayo un paso, al pulsar TEC1.
 */
static void avanzarSecuencia( void )
{
   if( enExtremoFinal == FALSE ) {
      enExtremoFinal  = TRUE;
      objetivoDecimas = CONSIGNA_MAX * 10;
      informar( "PASO: yendo al extremo opuesto" );
   } else {
      enExtremoFinal = FALSE;
      repeticion++;
      objetivoDecimas = CONSIGNA_MIN * 10;

      if( repeticion >= REPETICIONES ) {
         finalizando = TRUE;
         informar( "PASO: ultima vuelta al extremo inicial" );
      } else {
         informar( "PASO: volviendo al extremo inicial. Anotar tambien el "
                   "error de retorno al cero" );
      }
   }
   estado = ESTADO_MOVIENDO;
}

/**
 * @brief Lleva el servomotor al extremo inicial y termina el ensayo.
 *
 * Es el estado seguro: una pose alcanzable con la consigna mantenida, no
 * dejar de escribir en el servomotor.
 */
static void abortar( void )
{
   enExtremoFinal  = FALSE;
   finalizando     = TRUE;
   objetivoDecimas = CONSIGNA_MIN * 10;
   estado          = ESTADO_MOVIENDO;
   informar( "PASO: abortado por el operador, volviendo al extremo inicial" );
}

/*==================[funcion principal]======================================*/

int main( void )
{
   boardConfig();
   uartConfig( UART_USB, UART_BAUDIOS );

   /* servoConfig se llama dos veces: primero habilita el periferico (el
    * primer argumento se ignora) y despues cada salida que se va a usar.
    * Ocupa los temporizadores 1, 2 y 3 del LPC4337, no el SCTimer.         */
   if( servoConfig( 0, SERVO_ENABLE ) == FALSE ) {
      informar( "ERROR: no se pudo habilitar el periferico de servos" );
      while( TRUE ) {}
   }
   if( servoConfig( SERVO_ENSAYO, SERVO_ENABLE_OUTPUT ) == FALSE ) {
      informar( "ERROR: no se pudo habilitar la salida del servo" );
      while( TRUE ) {}
   }

   delayConfig( &temporizadorRampa,  PERIODO_RAMPA_MS );
   delayConfig( &temporizadorTeclas, PERIODO_TECLAS_MS );

   informar( "INIT: ensayo de barrido angular del servomotor MG996R" );
   snprintf( mensaje, sizeof( mensaje ),
             "INIT: consignas %d a %d, pulso %lu a %lu us, %d repeticiones",
             CONSIGNA_MIN, CONSIGNA_MAX,
             (unsigned long)pulsoEnMicrosegundos( CONSIGNA_MIN ),
             (unsigned long)pulsoEnMicrosegundos( CONSIGNA_MAX ),
             REPETICIONES );
   informar( mensaje );
   informar( "INIT: TEC1 avanza, TEC2 y TEC3 ajustan -1 y +1, TEC4 aborta" );

   aplicarConsigna();

   while( TRUE ) {

      /*--- tarea de teclas --------------------------------------------*/
      if( delayRead( &temporizadorTeclas ) ) {

         bool_t tec1 = flancoDeTecla( TEC1, &previaTec1 );
         bool_t tec2 = flancoDeTecla( TEC2, &previaTec2 );
         bool_t tec3 = flancoDeTecla( TEC3, &previaTec3 );
         bool_t tec4 = flancoDeTecla( TEC4, &previaTec4 );

         if( tec4 == TRUE ) {
            abortar();
         } else if( estado == ESTADO_ESPERANDO_OPERADOR ) {

            if( tec2 == TRUE ) {
               consignaDecimas -= TRIM * 10;
               aplicarConsigna();
               objetivoDecimas = consignaDecimas;
               informarPaso();
            }
            if( tec3 == TRUE ) {
               consignaDecimas += TRIM * 10;
               aplicarConsigna();
               objetivoDecimas = consignaDecimas;
               informarPaso();
            }
            if( tec1 == TRUE ) {
               avanzarSecuencia();
            }
         }
      }

      /*--- tarea de rampa ---------------------------------------------*/
      if( delayRead( &temporizadorRampa ) ) {

         if( estado == ESTADO_MOVIENDO ) {

            if( consignaDecimas < objetivoDecimas ) {
               consignaDecimas += PASO_RAMPA_DECIMAS;
               if( consignaDecimas > objetivoDecimas ) {
                  consignaDecimas = objetivoDecimas;
               }
            } else if( consignaDecimas > objetivoDecimas ) {
               consignaDecimas -= PASO_RAMPA_DECIMAS;
               if( consignaDecimas < objetivoDecimas ) {
                  consignaDecimas = objetivoDecimas;
               }
            }

            aplicarConsigna();

            if( consignaDecimas == objetivoDecimas ) {
               if( finalizando == TRUE ) {
                  estado = ESTADO_FIN;
                  informar( "DATA: ensayo terminado. Promediar las tres "
                            "lecturas y volcarlas en la Tabla 9 del informe" );
               } else {
                  estado = ESTADO_ASENTANDO;
                  delayConfig( &temporizadorAsentamiento, ASENTAMIENTO_MS );
               }
            }
         }
      }

      /*--- tarea de asentamiento --------------------------------------*/
      if( estado == ESTADO_ASENTANDO ) {
         if( delayRead( &temporizadorAsentamiento ) ) {
            estado = ESTADO_ESPERANDO_OPERADOR;
            informarPaso();
         }
      }
   }

   return 0;
}

/*==================[fin del archivo]========================================*/
