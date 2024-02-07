################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (11.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../PeripheralDrivers/Src/oled.c 

OBJS += \
./PeripheralDrivers/Src/oled.o 

C_DEPS += \
./PeripheralDrivers/Src/oled.d 


# Each subdirectory must supply rules for building sources it contributes
PeripheralDrivers/Src/%.o PeripheralDrivers/Src/%.su PeripheralDrivers/Src/%.cyclo: ../PeripheralDrivers/Src/%.c PeripheralDrivers/Src/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -g3 -DDEBUG -DUSE_HAL_DRIVER -DSTM32F407xx -c -I../Core/Inc -I../Drivers/STM32F4xx_HAL_Driver/Inc -I../Drivers/STM32F4xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32F4xx/Include -I../Drivers/CMSIS/Include -I../Middlewares/Third_Party/FreeRTOS/Source/include -I../Middlewares/Third_Party/FreeRTOS/Source/CMSIS_RTOS_V2 -I../Middlewares/Third_Party/FreeRTOS/Source/portable/GCC/ARM_CM4F -O0 -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-PeripheralDrivers-2f-Src

clean-PeripheralDrivers-2f-Src:
	-$(RM) ./PeripheralDrivers/Src/oled.cyclo ./PeripheralDrivers/Src/oled.d ./PeripheralDrivers/Src/oled.o ./PeripheralDrivers/Src/oled.su

.PHONY: clean-PeripheralDrivers-2f-Src

