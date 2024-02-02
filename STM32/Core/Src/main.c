/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2024 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "cmsis_os.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "oled.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/
TIM_HandleTypeDef htim1;
TIM_HandleTypeDef htim2;
TIM_HandleTypeDef htim3;
TIM_HandleTypeDef htim8;

UART_HandleTypeDef huart3;

/* Definitions for defaultTask */
osThreadId_t defaultTaskHandle;
const osThreadAttr_t defaultTask_attributes = {
  .name = "defaultTask",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityNormal,
};
/* Definitions for oled */
osThreadId_t oledHandle;
const osThreadAttr_t oled_attributes = {
  .name = "oled",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityLow,
};
/* Definitions for Motor */
osThreadId_t MotorHandle;
const osThreadAttr_t Motor_attributes = {
  .name = "Motor",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityLow,
};
/* Definitions for encoder1 */
osThreadId_t encoder1Handle;
const osThreadAttr_t encoder1_attributes = {
  .name = "encoder1",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityLow,
};
/* Definitions for encoder2 */
osThreadId_t encoder2Handle;
const osThreadAttr_t encoder2_attributes = {
  .name = "encoder2",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityLow,
};

uint32_t leftEncoderVal, rightEncoderVal;
/* USER CODE BEGIN PV */

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
static void MX_GPIO_Init(void);
static void MX_TIM2_Init(void);
static void MX_TIM8_Init(void);
static void MX_USART3_UART_Init(void);
static void MX_TIM1_Init(void);
static void MX_TIM3_Init(void);
void StartDefaultTask(void *argument);
void OLEDDisplay(void *argument);
void MOTOR(void *argument);
void LEncoder(void *argument);
void REncoder(void *argument);

/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */
uint8_t aRxBuffer[20];
/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_TIM2_Init();
  MX_TIM8_Init();
  MX_USART3_UART_Init();
  MX_TIM1_Init();
  MX_TIM3_Init();
  /* USER CODE BEGIN 2 */
  OLED_Init();
  /* USER CODE END 2 */
  HAL_UART_Receive_IT(&huart3,(uint8_t *) aRxBuffer,10);
  /* Init scheduler */
  osKernelInitialize();

  /* USER CODE BEGIN RTOS_MUTEX */
  /* add mutexes, ... */
  /* USER CODE END RTOS_MUTEX */

  /* USER CODE BEGIN RTOS_SEMAPHORES */
  /* add semaphores, ... */
  /* USER CODE END RTOS_SEMAPHORES */

  /* USER CODE BEGIN RTOS_TIMERS */
  /* start timers, add new ones, ... */
  /* USER CODE END RTOS_TIMERS */

  /* USER CODE BEGIN RTOS_QUEUES */
  /* add queues, ... */
  /* USER CODE END RTOS_QUEUES */

  /* Create the thread(s) */
  /* creation of defaultTask */
  defaultTaskHandle = osThreadNew(StartDefaultTask, NULL, &defaultTask_attributes);

  /* creation of oled */
  oledHandle = osThreadNew(OLEDDisplay, NULL, &oled_attributes);

  /* creation of Motor */
  MotorHandle = osThreadNew(MOTOR, NULL, &Motor_attributes);

  /* creation of encoder1 */
  encoder1Handle = osThreadNew(LEncoder, NULL, &encoder1_attributes);

  /* creation of encoder2 */
  encoder2Handle = osThreadNew(REncoder, NULL, &encoder2_attributes);

  /* USER CODE BEGIN RTOS_THREADS */
  /* add threads, ... */
  /* USER CODE END RTOS_THREADS */

  /* USER CODE BEGIN RTOS_EVENTS */
  /* add events, ... */
  /* USER CODE END RTOS_EVENTS */

  /* Start scheduler */
  osKernelStart();

  /* We should never get here as control is now taken by the scheduler */
  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV1;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV1;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_0) != HAL_OK)
  {
    Error_Handler();
  }
}

/**
  * @brief TIM1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM1_Init(void)
{

  /* USER CODE BEGIN TIM1_Init 0 */

  /* USER CODE END TIM1_Init 0 */

  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};
  TIM_BreakDeadTimeConfigTypeDef sBreakDeadTimeConfig = {0};

  /* USER CODE BEGIN TIM1_Init 1 */

  /* USER CODE END TIM1_Init 1 */
  htim1.Instance = TIM1;
  htim1.Init.Prescaler = 160;
  htim1.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim1.Init.Period = 1000;
  htim1.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim1.Init.RepetitionCounter = 0;
  htim1.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_PWM_Init(&htim1) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim1, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 0;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  sConfigOC.OCIdleState = TIM_OCIDLESTATE_RESET;
  sConfigOC.OCNIdleState = TIM_OCNIDLESTATE_RESET;
  if (HAL_TIM_PWM_ConfigChannel(&htim1, &sConfigOC, TIM_CHANNEL_4) != HAL_OK)
  {
    Error_Handler();
  }
  sBreakDeadTimeConfig.OffStateRunMode = TIM_OSSR_DISABLE;
  sBreakDeadTimeConfig.OffStateIDLEMode = TIM_OSSI_DISABLE;
  sBreakDeadTimeConfig.LockLevel = TIM_LOCKLEVEL_OFF;
  sBreakDeadTimeConfig.DeadTime = 0;
  sBreakDeadTimeConfig.BreakState = TIM_BREAK_DISABLE;
  sBreakDeadTimeConfig.BreakPolarity = TIM_BREAKPOLARITY_HIGH;
  sBreakDeadTimeConfig.AutomaticOutput = TIM_AUTOMATICOUTPUT_DISABLE;
  if (HAL_TIMEx_ConfigBreakDeadTime(&htim1, &sBreakDeadTimeConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM1_Init 2 */

  /* USER CODE END TIM1_Init 2 */
  HAL_TIM_MspPostInit(&htim1);

}

/**
  * @brief TIM2 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM2_Init(void)
{

  /* USER CODE BEGIN TIM2_Init 0 */

  /* USER CODE END TIM2_Init 0 */

  TIM_Encoder_InitTypeDef sConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM2_Init 1 */

  /* USER CODE END TIM2_Init 1 */
  htim2.Instance = TIM2;
  htim2.Init.Prescaler = 0;
  htim2.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim2.Init.Period = 65535;
  htim2.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim2.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  sConfig.EncoderMode = TIM_ENCODERMODE_TI12;
  sConfig.IC1Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC1Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC1Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC1Filter = 10;
  sConfig.IC2Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC2Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC2Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC2Filter = 10;
  if (HAL_TIM_Encoder_Init(&htim2, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim2, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM2_Init 2 */

  /* USER CODE END TIM2_Init 2 */

}

/**
  * @brief TIM3 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM3_Init(void)
{

  /* USER CODE BEGIN TIM3_Init 0 */

  /* USER CODE END TIM3_Init 0 */

  TIM_Encoder_InitTypeDef sConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};

  /* USER CODE BEGIN TIM3_Init 1 */

  /* USER CODE END TIM3_Init 1 */
  htim3.Instance = TIM3;
  htim3.Init.Prescaler = 0;
  htim3.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim3.Init.Period = 65535;
  htim3.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim3.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  sConfig.EncoderMode = TIM_ENCODERMODE_TI12;
  sConfig.IC1Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC1Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC1Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC1Filter = 10;
  sConfig.IC2Polarity = TIM_ICPOLARITY_RISING;
  sConfig.IC2Selection = TIM_ICSELECTION_DIRECTTI;
  sConfig.IC2Prescaler = TIM_ICPSC_DIV1;
  sConfig.IC2Filter = 10;
  if (HAL_TIM_Encoder_Init(&htim3, &sConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim3, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM3_Init 2 */

  /* USER CODE END TIM3_Init 2 */

}

/**
  * @brief TIM8 Initialization Function
  * @param None
  * @retval None
  */
static void MX_TIM8_Init(void)
{

  /* USER CODE BEGIN TIM8_Init 0 */

  /* USER CODE END TIM8_Init 0 */

  TIM_ClockConfigTypeDef sClockSourceConfig = {0};
  TIM_MasterConfigTypeDef sMasterConfig = {0};
  TIM_OC_InitTypeDef sConfigOC = {0};
  TIM_BreakDeadTimeConfigTypeDef sBreakDeadTimeConfig = {0};

  /* USER CODE BEGIN TIM8_Init 1 */

  /* USER CODE END TIM8_Init 1 */
  htim8.Instance = TIM8;
  htim8.Init.Prescaler = 0;
  htim8.Init.CounterMode = TIM_COUNTERMODE_UP;
  htim8.Init.Period = 7199;
  htim8.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
  htim8.Init.RepetitionCounter = 0;
  htim8.Init.AutoReloadPreload = TIM_AUTORELOAD_PRELOAD_DISABLE;
  if (HAL_TIM_Base_Init(&htim8) != HAL_OK)
  {
    Error_Handler();
  }
  sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;
  if (HAL_TIM_ConfigClockSource(&htim8, &sClockSourceConfig) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_Init(&htim8) != HAL_OK)
  {
    Error_Handler();
  }
  sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
  sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
  if (HAL_TIMEx_MasterConfigSynchronization(&htim8, &sMasterConfig) != HAL_OK)
  {
    Error_Handler();
  }
  sConfigOC.OCMode = TIM_OCMODE_PWM1;
  sConfigOC.Pulse = 0;
  sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
  sConfigOC.OCNPolarity = TIM_OCNPOLARITY_HIGH;
  sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
  sConfigOC.OCIdleState = TIM_OCIDLESTATE_RESET;
  sConfigOC.OCNIdleState = TIM_OCNIDLESTATE_RESET;
  if (HAL_TIM_PWM_ConfigChannel(&htim8, &sConfigOC, TIM_CHANNEL_1) != HAL_OK)
  {
    Error_Handler();
  }
  if (HAL_TIM_PWM_ConfigChannel(&htim8, &sConfigOC, TIM_CHANNEL_2) != HAL_OK)
  {
    Error_Handler();
  }
  sBreakDeadTimeConfig.OffStateRunMode = TIM_OSSR_DISABLE;
  sBreakDeadTimeConfig.OffStateIDLEMode = TIM_OSSI_DISABLE;
  sBreakDeadTimeConfig.LockLevel = TIM_LOCKLEVEL_OFF;
  sBreakDeadTimeConfig.DeadTime = 0;
  sBreakDeadTimeConfig.BreakState = TIM_BREAK_DISABLE;
  sBreakDeadTimeConfig.BreakPolarity = TIM_BREAKPOLARITY_HIGH;
  sBreakDeadTimeConfig.AutomaticOutput = TIM_AUTOMATICOUTPUT_DISABLE;
  if (HAL_TIMEx_ConfigBreakDeadTime(&htim8, &sBreakDeadTimeConfig) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN TIM8_Init 2 */

  /* USER CODE END TIM8_Init 2 */
  HAL_TIM_MspPostInit(&htim8);

}

/**
  * @brief USART3 Initialization Function
  * @param None
  * @retval None
  */
static void MX_USART3_UART_Init(void)
{

  /* USER CODE BEGIN USART3_Init 0 */

  /* USER CODE END USART3_Init 0 */

  /* USER CODE BEGIN USART3_Init 1 */

  /* USER CODE END USART3_Init 1 */
  huart3.Instance = USART3;
  huart3.Init.BaudRate = 115200;
  huart3.Init.WordLength = UART_WORDLENGTH_8B;
  huart3.Init.StopBits = UART_STOPBITS_1;
  huart3.Init.Parity = UART_PARITY_NONE;
  huart3.Init.Mode = UART_MODE_TX_RX;
  huart3.Init.HwFlowCtl = UART_HWCONTROL_NONE;
  huart3.Init.OverSampling = UART_OVERSAMPLING_16;
  if (HAL_UART_Init(&huart3) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN USART3_Init 2 */

  /* USER CODE END USART3_Init 2 */

}

/**
  * @brief GPIO Initialization Function
  * @param None
  * @retval None
  */
static void MX_GPIO_Init(void)
{
  GPIO_InitTypeDef GPIO_InitStruct = {0};
/* USER CODE BEGIN MX_GPIO_Init_1 */
/* USER CODE END MX_GPIO_Init_1 */

  /* GPIO Ports Clock Enable */
  __HAL_RCC_GPIOE_CLK_ENABLE();
  __HAL_RCC_GPIOA_CLK_ENABLE();
  __HAL_RCC_GPIOC_CLK_ENABLE();
  __HAL_RCC_GPIOB_CLK_ENABLE();

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOE, OLED_SCL_Pin|OLED_SDA_Pin|OLED_RST_Pin|OLED_DC_Pin
                          |LED3_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pin Output Level */
  HAL_GPIO_WritePin(GPIOA, AIN2_Pin|AIN1_Pin|BIN1_Pin|BIN2_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pins : OLED_SCL_Pin OLED_SDA_Pin OLED_RST_Pin OLED_DC_Pin
                           LED3_Pin */
  GPIO_InitStruct.Pin = OLED_SCL_Pin|OLED_SDA_Pin|OLED_RST_Pin|OLED_DC_Pin
                          |LED3_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOE, &GPIO_InitStruct);

  /*Configure GPIO pins : AIN2_Pin AIN1_Pin BIN1_Pin BIN2_Pin */
  GPIO_InitStruct.Pin = AIN2_Pin|AIN1_Pin|BIN1_Pin|BIN2_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

/* USER CODE BEGIN MX_GPIO_Init_2 */
/* USER CODE END MX_GPIO_Init_2 */
}

void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
	// Prevent unused argument(s) compilation warning
	UNUSED(huart);

	HAL_UART_Transmit(&huart3, (uint8_t *)aRxBuffer,10,0xFFFF);
}

/* USER CODE BEGIN 4 */

/* USER CODE END 4 */

/* USER CODE BEGIN Header_StartDefaultTask */
/**
  * @brief  Function implementing the defaultTask thread.
  * @param  argument: Not used
  * @retval None
  */
/* USER CODE END Header_StartDefaultTask */
void StartDefaultTask(void *argument)
{
  /* USER CODE BEGIN 5 */
  /* Infinite loop */
	uint8_t ch = 'A';
  for(;;)
  {
	HAL_UART_Transmit(&huart3,(uint8_t *)&ch,1,0xFFFF);
	if (ch<'Z')
	{
		ch++;

	}
	else ch = 'A';
	HAL_GPIO_TogglePin(LED3_GPIO_Port, LED3_Pin);
    osDelay(5000);
  }
  /* USER CODE END 5 */
}

/* USER CODE BEGIN Header_OLEDDisplay */
/**
* @brief Function implementing the oled thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_OLEDDisplay */
void OLEDDisplay(void *argument)
{
	/* USER CODE BEGIN show */
	uint8_t hello[20]= "Testing RN!\0";
//	char speedStringL[20];
//	char speedStringR[20];

	/* Infinite loop */
	for(;;)
	{
//	  OLED_ShowString(10,10, hello);H
	  sprintf(hello,"%s\0", aRxBuffer);
	  OLED_ShowString(10,10, hello);
	  // Display motor speed revolution
//	  sprintf(speedStringL, "SpeedL: %d", leftEncoderVal);
//	  OLED_ShowString(10, 30, (uint8_t*)speedStringL);
//	  sprintf(speedStringR, "SpeedR: %d", rightEncoderVal);
//	  OLED_ShowString(10, 50, (uint8_t*)speedStringR);
	  OLED_Refresh_Gram();
	  osDelay(1);
	}
	  /* USER CODE END show */
}

/* USER CODE BEGIN Header_MOTOR */
/**
* @brief Function implementing the Motor thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_MOTOR */
void MOTOR(void *argument)
{
		uint16_t pwmVal  =0;
		HAL_TIM_PWM_Start(&htim8, TIM_CHANNEL_1);
		HAL_TIM_PWM_Start(&htim8, TIM_CHANNEL_2);
		HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_4);

// For forward and backwards testing
	/*
	  for(;;)
	  {
		  while(pwmVal<4000)
		  {
			  // Left Motor (Motor A)
			  HAL_GPIO_WritePin(GPIOA, AIN2_Pin, GPIO_PIN_SET);
			  HAL_GPIO_WritePin(GPIOA,AIN1_Pin, GPIO_PIN_RESET);

			  // Right Motor (Motor B)
			  HAL_GPIO_WritePin(GPIOA, BIN2_Pin, GPIO_PIN_SET);
			  HAL_GPIO_WritePin(GPIOA, BIN1_Pin, GPIO_PIN_RESET);

			  pwmVal++;
			  __HAL_TIM_SetCompare(&htim8,TIM_CHANNEL_1,pwmVal);
			  __HAL_TIM_SetCompare(&htim8,TIM_CHANNEL_2,pwmVal);

			  osDelay(10);

		  }
		  //Anticlock
		  while(pwmVal>0)
		  {
			  // Left Motor
			  HAL_GPIO_WritePin(GPIOA, AIN2_Pin, GPIO_PIN_RESET);
			  HAL_GPIO_WritePin(GPIOA, AIN1_Pin, GPIO_PIN_SET);

			  // Right Motor
			  HAL_GPIO_WritePin(GPIOA, BIN2_Pin, GPIO_PIN_RESET);
			  HAL_GPIO_WritePin(GPIOA, BIN1_Pin, GPIO_PIN_SET);

			  pwmVal--;
			  __HAL_TIM_SetCompare(&htim8,TIM_CHANNEL_1,pwmVal);
			  __HAL_TIM_SetCompare(&htim8,TIM_CHANNEL_2,pwmVal);
			  osDelay(10);

		  }
		  osDelay(1);
	  } */

// For backwheels turn testing
		/*
		for(;;)
			  {
				  while(pwmVal<1600)
				  {
					  // Left Motor (Motor A)
					  HAL_GPIO_WritePin(GPIOA, AIN2_Pin, GPIO_PIN_RESET);
					  HAL_GPIO_WritePin(GPIOA, AIN1_Pin, GPIO_PIN_SET);

					  // Right Motor (Motor B)
					  HAL_GPIO_WritePin(GPIOA, BIN2_Pin, GPIO_PIN_SET);
					  HAL_GPIO_WritePin(GPIOA, BIN1_Pin, GPIO_PIN_RESET);

					  pwmVal++;
					  __HAL_TIM_SetCompare(&htim8,TIM_CHANNEL_1,pwmVal);
					  __HAL_TIM_SetCompare(&htim8,TIM_CHANNEL_2,pwmVal);

					  osDelay(10);

				  }
				  while(pwmVal>0)
				  {
					  // Left Motor
					  HAL_GPIO_WritePin(GPIOA, AIN2_Pin, GPIO_PIN_SET);
					  HAL_GPIO_WritePin(GPIOA, AIN1_Pin, GPIO_PIN_RESET);

					  // Right Motor
					  HAL_GPIO_WritePin(GPIOA, BIN2_Pin, GPIO_PIN_SET);
					  HAL_GPIO_WritePin(GPIOA, BIN1_Pin, GPIO_PIN_RESET);

					//  pwmVal--;
					  __HAL_TIM_SetCompare(&htim8,TIM_CHANNEL_1,pwmVal);
					  __HAL_TIM_SetCompare(&htim8,TIM_CHANNEL_2,pwmVal);
					  osDelay(10);

				  }
				  osDelay(1);
			  }
			  */
		  for(;;)
		  {
			  while(pwmVal<1010)
			  {
				  // Left Motor (Motor A)
				  HAL_GPIO_WritePin(GPIOA, AIN2_Pin, GPIO_PIN_RESET);
				  HAL_GPIO_WritePin(GPIOA,AIN1_Pin, GPIO_PIN_SET);

				  // Right Motor (Motor B)
				  HAL_GPIO_WritePin(GPIOA, BIN2_Pin, GPIO_PIN_RESET);
				  HAL_GPIO_WritePin(GPIOA, BIN1_Pin, GPIO_PIN_SET);

				  pwmVal++;

				  if (pwmVal>=1000){
				//	  htim1.Instance->CCR4 = 145;
				//	  osDelay(2000);
					  htim1.Instance->CCR4 = 147;
					  osDelay(2000);
				//	  htim1.Instance->CCR4 = 145; //center
				//	  osDelay(5000);
				  }

				  __HAL_TIM_SetCompare(&htim8,TIM_CHANNEL_1,pwmVal);
				  __HAL_TIM_SetCompare(&htim8,TIM_CHANNEL_2,pwmVal+800);

				  osDelay(10);

			  }
			  osDelay(1);
			  //Anticlock
			  /*
			  while(pwmVal>0)
			  {
				  // Left Motor
				  HAL_GPIO_WritePin(GPIOA, AIN2_Pin, GPIO_PIN_RESET);
				  HAL_GPIO_WritePin(GPIOA, AIN1_Pin, GPIO_PIN_SET);

				  // Right Motor
				  HAL_GPIO_WritePin(GPIOA, BIN2_Pin, GPIO_PIN_RESET);
				  HAL_GPIO_WritePin(GPIOA, BIN1_Pin, GPIO_PIN_SET);

				  pwmVal--;
				  __HAL_TIM_SetCompare(&htim8,TIM_CHANNEL_1,pwmVal);
				  __HAL_TIM_SetCompare(&htim8,TIM_CHANNEL_2,pwmVal);
				  osDelay(10);

			  }
			  osDelay(1);
			  */
		  }



}

/* USER CODE BEGIN Header_LEncoder */
/**
* @brief Function implementing the encoder1 thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_LEncoder */
void LEncoder(void *argument)
{
		HAL_TIM_Encoder_Start(&htim2, TIM_CHANNEL_ALL);
		int cnt2;
		int dirL = 1;
		int diff;
		uint32_t tick = HAL_GetTick();
		/* Infinite loop */
		for (;;) {
			if (HAL_GetTick() - tick > 10L) {
				cnt2 = __HAL_TIM_GET_COUNTER(&htim2);

				if (cnt2 > 32000) {
					dirL = 1;
					diff = (65536 - cnt2);
				} else {
					dirL = -1;
					diff = cnt2;
				}
				if (dirL == 1) {
					leftEncoderVal -= diff;
				} else {
					leftEncoderVal += diff;
				}

				__HAL_TIM_SET_COUNTER(&htim2, 0);

				tick = HAL_GetTick();
			}
		}
}

/* USER CODE BEGIN Header_REncoder */
/**
* @brief Function implementing the encoder2 thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_REncoder */
void REncoder(void *argument)
{
		HAL_TIM_Encoder_Start(&htim3, TIM_CHANNEL_ALL);
		int cnt1;
		int dirR = 1;
		int diff;
		uint32_t tick = HAL_GetTick();
		/* Infinite loop */
		for (;;) {
			if (HAL_GetTick() - tick > 10L) {
				cnt1 = __HAL_TIM_GET_COUNTER(&htim3);
				if (cnt1 > 32000) {
					dirR = 1;
					diff = (65536 - cnt1);
				} else {
					dirR = -1;
					diff = cnt1;
				}

				if (dirR == 1) {
					rightEncoderVal += diff;
				} else {
					rightEncoderVal -= diff;
				}

				__HAL_TIM_SET_COUNTER(&htim3, 0);

				tick = HAL_GetTick();
			}
		}
}

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1){
  }
  /* USER CODE END Error_Handler_Debug */
}

#ifdef  USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
