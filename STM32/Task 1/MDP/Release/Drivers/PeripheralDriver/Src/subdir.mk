################################################################################
# Automatically-generated file. Do not edit!
# Toolchain: GNU Tools for STM32 (12.3.rel1)
################################################################################

# Add inputs and outputs from these tool invocations to the build variables 
C_SRCS += \
../Drivers/PeripheralDriver/Src/oled.c 

OBJS += \
./Drivers/PeripheralDriver/Src/oled.o 

C_DEPS += \
./Drivers/PeripheralDriver/Src/oled.d 


# Each subdirectory must supply rules for building sources it contributes
Drivers/PeripheralDriver/Src/%.o Drivers/PeripheralDriver/Src/%.su Drivers/PeripheralDriver/Src/%.cyclo: ../Drivers/PeripheralDriver/Src/%.c Drivers/PeripheralDriver/Src/subdir.mk
	arm-none-eabi-gcc "$<" -mcpu=cortex-m4 -std=gnu11 -DUSE_HAL_DRIVER -DSTM32F407xx -c -I../Core/Inc -I../Drivers/STM32F4xx_HAL_Driver/Inc -I../Drivers/STM32F4xx_HAL_Driver/Inc/Legacy -I../Drivers/CMSIS/Device/ST/STM32F4xx/Include -I../Drivers/CMSIS/Include -I"C:/Users/User/Documents/MDP/Main/MDPGrp29/Task 1/MDP/Drivers/PeripheralDriver/Inc" -I../Middlewares/Third_Party/FreeRTOS/Source/include -I../Middlewares/Third_Party/FreeRTOS/Source/CMSIS_RTOS_V2 -I../Middlewares/Third_Party/FreeRTOS/Source/portable/GCC/ARM_CM4F -Os -ffunction-sections -fdata-sections -Wall -fstack-usage -fcyclomatic-complexity -MMD -MP -MF"$(@:%.o=%.d)" -MT"$@" --specs=nano.specs -mfpu=fpv4-sp-d16 -mfloat-abi=hard -mthumb -o "$@"

clean: clean-Drivers-2f-PeripheralDriver-2f-Src

clean-Drivers-2f-PeripheralDriver-2f-Src:
	-$(RM) ./Drivers/PeripheralDriver/Src/oled.cyclo ./Drivers/PeripheralDriver/Src/oled.d ./Drivers/PeripheralDriver/Src/oled.o ./Drivers/PeripheralDriver/Src/oled.su

.PHONY: clean-Drivers-2f-PeripheralDriver-2f-Src

