#include "sapi.h"
#include <stdint.h>
#define ADC_CH_BASE CH2
#define ADC_CH_HOMBRO CH1
#define ADC_CH_CODO CH3

void adc_init() {
    adcInit(ADC_ENABLE);
}
uint16_t adc_read_base() {
    return adcRead(ADC_CH_BASE);
}
uint16_t adc_read_hombro() {
    return adcRead(ADC_CH_HOMBRO);
}
uint16_t adc_read_codo() {
    return adcRead(ADC_CH_CODO);
}