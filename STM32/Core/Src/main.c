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
I2C_HandleTypeDef hi2c1;

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
/* Definitions for startGyro */
osThreadId_t startGyroHandle;
const osThreadAttr_t startGyro_attributes = {
  .name = "startGyro",
  .stack_size = 128 * 4,
  .priority = (osPriority_t) osPriorityLow,
};
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
static void MX_I2C1_Init(void);
void StartDefaultTask(void *argument);
void OLEDDisplay(void *argument);
void MOTOR(void *argument);
void LEncoder(void *argument);
void REncoder(void *argument);
void startGyroTask(void *argument);

/* USER CODE BEGIN PFP */
// Gyro
double total_angle=0;
uint8_t gyroBuffer[20];
uint8_t ICMAddress = 0x68;

// movement
uint16_t pwmVal_servo = 149;
uint16_t pwmVal_R = 0;
uint16_t pwmVal_L = 0;
int times_acceptable=0;
int e_brake = 0;

// MotorEncoder
int32_t rightEncoderVal = 0, leftEncoderVal = 0;
int32_t rightTarget = 0, leftTarget = 0;
double target_angle=0;
/* USER CODE END PFP */


/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

/* USER CODE END 0 */

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
  MX_I2C1_Init();
  /* USER CODE BEGIN 2 */
  OLED_Init();
  /* USER CODE END 2 */

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

  /* creation of startGyro */
  startGyroHandle = osThreadNew(startGyroTask, NULL, &startGyro_attributes);

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
  * @brief I2C1 Initialization Function
  * @param None
  * @retval None
  */
static void MX_I2C1_Init(void)
{

  /* USER CODE BEGIN I2C1_Init 0 */

  /* USER CODE END I2C1_Init 0 */

  /* USER CODE BEGIN I2C1_Init 1 */

  /* USER CODE END I2C1_Init 1 */
  hi2c1.Instance = I2C1;
  hi2c1.Init.ClockSpeed = 100000;
  hi2c1.Init.DutyCycle = I2C_DUTYCYCLE_2;
  hi2c1.Init.OwnAddress1 = 0;
  hi2c1.Init.AddressingMode = I2C_ADDRESSINGMODE_7BIT;
  hi2c1.Init.DualAddressMode = I2C_DUALADDRESS_DISABLE;
  hi2c1.Init.OwnAddress2 = 0;
  hi2c1.Init.GeneralCallMode = I2C_GENERALCALL_DISABLE;
  hi2c1.Init.NoStretchMode = I2C_NOSTRETCH_DISABLE;
  if (HAL_I2C_Init(&hi2c1) != HAL_OK)
  {
    Error_Handler();
  }
  /* USER CODE BEGIN I2C1_Init 2 */

  /* USER CODE END I2C1_Init 2 */

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
  HAL_GPIO_WritePin(GPIOB, Buzzer_Pin, GPIO_PIN_RESET);

  /*Configure GPIO pins : OLED_SCL_Pin OLED_SDA_Pin OLED_RST_Pin OLED_DC_Pin
                           LED3_Pin */
  GPIO_InitStruct.Pin = OLED_SCL_Pin|OLED_SDA_Pin|OLED_RST_Pin|OLED_DC_Pin
                          |LED3_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOE, &GPIO_InitStruct);

  GPIO_InitStruct.Pin = Buzzer_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

  /*Configure GPIO pins : AIN2_Pin AIN1_Pin BIN1_Pin BIN2_Pin */
  GPIO_InitStruct.Pin = AIN2_Pin|AIN1_Pin|BIN1_Pin|BIN2_Pin;
  GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
  GPIO_InitStruct.Pull = GPIO_NOPULL;
  GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
  HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

/* USER CODE BEGIN MX_GPIO_Init_2 */
/* USER CODE END MX_GPIO_Init_2 */
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

void readByte(uint8_t addr, uint8_t* data){
	gyroBuffer[0] = addr;
	HAL_I2C_Master_Transmit(&hi2c1, ICMAddress<<1, gyroBuffer, 1, 10);
	HAL_I2C_Master_Receive(&hi2c1, ICMAddress<<1, data, 2, 20);
}

void writeByte(uint8_t addr, uint8_t data){
	gyroBuffer[0] = addr;
	gyroBuffer[1] = data;
	HAL_I2C_Master_Transmit(&hi2c1, ICMAddress << 1, gyroBuffer, 2, 20);
}

void gyroInit(){
	writeByte(0x06, 0x00);
	osDelay(10);
	writeByte(0x03, 0x80);
	osDelay(10);
	writeByte(0x07, 0x07);
	osDelay(10);
	writeByte(0x06, 0x01);
	osDelay(10);
	writeByte(0x7F, 0x20);
	osDelay(10);
	writeByte(0x01, 0x2F);
	osDelay(10);
	writeByte(0x0, 0x00);
	osDelay(10);
	writeByte(0x7F, 0x00);
	osDelay(10);
	writeByte(0x07, 0x00);
	osDelay(10);
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
  /* USER CODE BEGIN OLEDDisplay */
	uint8_t righty[20] = {0};
  /* Infinite loop */
  for(;;)
  {
  //sprintf(righty,"Gyro: %d \0", (int)total_angle);
	int decimals = abs((int)((total_angle-(int)(total_angle))*1000));
	sprintf(righty,"Gyro: %d.%d \0", (int)total_angle, decimals);

	OLED_ShowString(10, 30, righty);
	OLED_Refresh_Gram();
    osDelay(1);
  }
  /*
	uint8_t hello[20]= "Testing RN!\0";
//	char speedStringL[20];
//	char speedStringR[20];

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
   */
}

/* USER CODE BEGIN Header_MOTOR */
/**
* @brief Function implementing the Motor thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_MOTOR */

void buzzerBeep()
{
	HAL_GPIO_TogglePin(GPIOB, GPIO_PIN_10); //Buzzer On
	HAL_Delay(500);
	HAL_GPIO_TogglePin(GPIOB, GPIO_PIN_10); //Buzzer Off
}

int PID_Control(int error, int right)
{
	if(right){//rightMotor
		if(error>0){//go forward
			HAL_GPIO_WritePin(GPIOA, BIN1_Pin, GPIO_PIN_SET); // set direction of rotation for wheel B- forward
			HAL_GPIO_WritePin(GPIOA, BIN2_Pin, GPIO_PIN_RESET);
		}else{//go backward
		    HAL_GPIO_WritePin(GPIOA, BIN1_Pin, GPIO_PIN_RESET); // set direction of rotation for wheel B - reverse
			HAL_GPIO_WritePin(GPIOA, BIN2_Pin, GPIO_PIN_SET);
		}
	}else{//leftMotor
		if(error>0){//go forward
			HAL_GPIO_WritePin(GPIOA, AIN1_Pin, GPIO_PIN_SET); // set direction of rotation for wheel A - forward
			HAL_GPIO_WritePin(GPIOA, AIN2_Pin, GPIO_PIN_RESET);
		}else{//go backward
		    HAL_GPIO_WritePin(GPIOA, AIN1_Pin, GPIO_PIN_RESET); // set direction of rotation for wheel A - reverse
			HAL_GPIO_WritePin(GPIOA, AIN2_Pin, GPIO_PIN_SET);
		}
	}

	error = abs(error);
	if(error > 2000){
		return 3000;
	}else if(error > 500){
		return 2000;
	}else if(error > 200){
		return 1400;
	}else if(error > 100){
		return 1000;
	}else if(error > 2){
		times_acceptable++;
		return 500;
	}else if(error >=1){
		times_acceptable++;
		return 0;
	}else{
		times_acceptable++;
		return 0;
	}
}

int PID_Angle(double errord, int right)
{
	int error = (int)(errord*10);
	if(right){//rightMotor
		if(error>0){//go forward
			HAL_GPIO_WritePin(GPIOA, BIN1_Pin, GPIO_PIN_SET); // set direction of rotation for wheel B- forward
			HAL_GPIO_WritePin(GPIOA, BIN2_Pin, GPIO_PIN_RESET);
		}else{//go backward
		    HAL_GPIO_WritePin(GPIOA, BIN1_Pin, GPIO_PIN_RESET); // set direction of rotation for wheel B - reverse
			HAL_GPIO_WritePin(GPIOA, BIN2_Pin, GPIO_PIN_SET);
		}
	}else{//leftMotor
		if(error<0){//go forward
			HAL_GPIO_WritePin(GPIOA, AIN1_Pin, GPIO_PIN_SET); // set direction of rotation for wheel A - forward
			HAL_GPIO_WritePin(GPIOA, AIN2_Pin, GPIO_PIN_RESET);
		}else{//go backward
		    HAL_GPIO_WritePin(GPIOA, AIN1_Pin, GPIO_PIN_RESET); // set direction of rotation for wheel A - reverse
			HAL_GPIO_WritePin(GPIOA, AIN2_Pin, GPIO_PIN_SET);
		}
	}

	error = abs(error);
	if(error > 300){
		return 3000;
	}else if(error > 200){
		return 2000;
	}else if(error > 150){
		return 1600;
	}else if(error > 100){
		return 1400;
	}else if(error >10){
		return 1000;
	}else if(error >=2){
		times_acceptable++;
		return 600;
	}else{
		times_acceptable++;
		return 0;
	}
}

int finishCheck(){
	if (times_acceptable > 20){
		e_brake = 1;
		pwmVal_L = pwmVal_R = 0;
		leftTarget = leftEncoderVal;
		rightTarget = rightEncoderVal;
		times_acceptable = 0;
	    osDelay(30); //og 300

		return 0;
	}
	return 1;
}


void MOTOR(void *argument)
{
	uint16_t pwmVal  = 1000;
	HAL_TIM_PWM_Start(&htim8, TIM_CHANNEL_1);
	HAL_TIM_PWM_Start(&htim8, TIM_CHANNEL_2);
	HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_4);

// For forward and backward testing
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
		  } */

// Test on straight movement as well as turning left/right
	  for(;;)
	  {
		  while(pwmVal<1100)
		  {
			  // Left Motor (Motor A)
			  HAL_GPIO_WritePin(GPIOA, AIN2_Pin, GPIO_PIN_RESET);
			  HAL_GPIO_WritePin(GPIOA,AIN1_Pin, GPIO_PIN_SET);

			  // Right Motor (Motor B)
			  HAL_GPIO_WritePin(GPIOA, BIN2_Pin, GPIO_PIN_RESET);
			  HAL_GPIO_WritePin(GPIOA, BIN1_Pin, GPIO_PIN_SET);

			  //pwmVal++;

			  if (pwmVal>=1000){
			//	  htim1.Instance->CCR4 = 145;
			//	  osDelay(2000);
				  htim1.Instance->CCR4 = 220; //right
				  osDelay(2000);
			//	  htim1.Instance->CCR4 = 145; //center
			//	  osDelay(2000);
		    //	  htim1.Instance->CCR4 = 85; //left
			//	  osDelay(2000);
			  }

			  __HAL_TIM_SetCompare(&htim8,TIM_CHANNEL_1,pwmVal);
			  __HAL_TIM_SetCompare(&htim8,TIM_CHANNEL_2,pwmVal+800); //added 800 more pwm on right motor
			  osDelay(10);
		  }
		  osDelay(1);
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

		  } */
		//osDelay(1);
	  }

	/*
	// With PID Implementation for Motors
		pwmVal_R = 0;
		pwmVal_L = 0;
		int straightCorrection=0;
		HAL_TIM_PWM_Start(&htim8, TIM_CHANNEL_1);
		HAL_TIM_PWM_Start(&htim8, TIM_CHANNEL_2);
		HAL_TIM_PWM_Start(&htim1, TIM_CHANNEL_4);
		htim1.Instance->CCR4 = 149; //Centre

		HAL_GPIO_WritePin(GPIOA, BIN1_Pin, GPIO_PIN_SET); // set direction of rotation for wheel B- forward
		HAL_GPIO_WritePin(GPIOA, BIN2_Pin, GPIO_PIN_RESET);
		HAL_GPIO_WritePin(GPIOA, AIN1_Pin, GPIO_PIN_SET); // set direction of rotation for wheel A - forward
		HAL_GPIO_WritePin(GPIOA, AIN2_Pin, GPIO_PIN_RESET);
		osDelay(100); //og 1000

		  for(;;)
		  {
				htim1.Instance->CCR4 = pwmVal_servo;
				double error_angle = target_angle - total_angle;
		//		if(aRxBuffer[0] = ' '){
		//			pwmVal_L = pwmVal_R = 0;
		//
		//		}else
					if (pwmVal_servo < 85){ //106 //TURN LEFT
					pwmVal_R = PID_Angle(error_angle, 1)*1.072;  //right is master
					pwmVal_L = pwmVal_R*(0.59); //left is slave

					if(error_angle>0){
						//go forward
						HAL_GPIO_WritePin(GPIOA, AIN1_Pin, GPIO_PIN_SET); // set direction of rotation for wheel A- forward
						HAL_GPIO_WritePin(GPIOA, AIN2_Pin, GPIO_PIN_RESET);
					}
					else{
						//go backward
						HAL_GPIO_WritePin(GPIOA, AIN1_Pin, GPIO_PIN_RESET); // set direction of rotation for wheel A - reverse
						HAL_GPIO_WritePin(GPIOA, AIN2_Pin, GPIO_PIN_SET);
					}
				}

				else if (pwmVal_servo > 200){ //230 //TURN RIGHT
					pwmVal_L = PID_Angle(error_angle, 0);
					pwmVal_R = pwmVal_L*(0.59); //right is slave

					if(error_angle<0){
						//go forward
						HAL_GPIO_WritePin(GPIOA, BIN1_Pin, GPIO_PIN_SET); // set direction of rotation for wheel B- forward
						HAL_GPIO_WritePin(GPIOA, BIN2_Pin, GPIO_PIN_RESET);
					}
					else{
						//go backward
						HAL_GPIO_WritePin(GPIOA, BIN1_Pin, GPIO_PIN_RESET); // set direction of rotation for wheel B - reverse
						HAL_GPIO_WritePin(GPIOA, BIN2_Pin, GPIO_PIN_SET);
					}
				}

				else {


					pwmVal_R = PID_Control(leftTarget - leftEncoderVal, 0)*1.072;
					if (abs(leftTarget - leftEncoderVal)>abs(rightTarget - rightEncoderVal)){
						straightCorrection++;
					}else{ straightCorrection--;}
					if (abs(leftTarget - leftEncoderVal)<100){
						straightCorrection=0;
					}
					pwmVal_L = PID_Control(rightTarget - rightEncoderVal, 1)+straightCorrection;


					if ((leftTarget - leftEncoderVal)<0){
						if (error_angle>5){ // if turn left, 106. right 230. left +. right -.
									pwmVal_servo=((19*5)/5 + 149);
								}
								else if(error_angle<-5){
									pwmVal_servo=((-19*5)/5 + 149);
								}else{
									pwmVal_servo=((19*error_angle)/5 + 149);
								}

					}else{
						if (error_angle>5){ // if turn left, 106. right 230. left +. right -.
									pwmVal_servo=((-19*5)/5 + 149);
								}
								else if(error_angle<-5){
									pwmVal_servo=((19*5)/5 + 149);
								}else{
									pwmVal_servo=((-19*error_angle)/5 + 149);
								}
					}


					//line correction equation is pwmVal = (19*error)/5 + 149
				}

				if(e_brake){
					pwmVal_L = pwmVal_R = 0;
					leftTarget = leftEncoderVal;
					rightTarget = rightEncoderVal;
				}

				__HAL_TIM_SetCompare(&htim8,TIM_CHANNEL_1,pwmVal_L);
				__HAL_TIM_SetCompare(&htim8,TIM_CHANNEL_2,pwmVal_R);
				osDelay(1);

				if (times_acceptable>1000){
					times_acceptable=1001;
				}

		  }
		  */
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

/* USER CODE BEGIN Header_startGyroTask */
/**
* @brief Function implementing the startGyro thread.
* @param argument: Not used
* @retval None
*/
/* USER CODE END Header_startGyroTask */
void startGyroTask(void *argument)
{
	/* USER CODE BEGIN StartGyroTask */
		gyroInit();
		uint8_t val[2] = {0,0};
		int16_t angular_speed = 0;
		uint32_t tick = 0;
		double offset = 0;
		double trash= 0;
		int i=0;

		//calibration phase
		while(i<100){
			osDelay(50);
			readByte(0x37, val);
			angular_speed = (val[0] << 8) | val[1];
			trash +=(double)((double)angular_speed)*((HAL_GetTick() - tick)/16400.0);
			offset += angular_speed;
			tick = HAL_GetTick();
			i++;
		}

		//calculate gyroscope bias(average offset)
		offset = offset/i;
		buzzerBeep();
		tick = HAL_GetTick();


	  /* Infinite loop */
	  for(;;)
	  {
			osDelay(50);
			readByte(0x37, val);
			angular_speed = (val[0] << 8) | val[1];
			//subtract gyroscope bias from measurement to compensate for drift
			total_angle +=(double)((double)angular_speed - offset)*((HAL_GetTick() - tick)/16400.0); //extra calibration +0.00003
			i -= angular_speed;
			tick = HAL_GetTick();
			i++;

	//		char hello[50] = {0};
	//		double diff = total_angle - old;
	//		int decimals = abs((int)((diff-(int)(diff))*10000));
	//		int offdeci = abs((int)((offset-(int)(offset))*10000));
	//		sprintf(hello,"G%d.%d: %d.%d \0", (int)offset,offdeci,(int)diff, decimals);
	//		old = total_angle;
	//		HAL_UART_Transmit(&huart3, hello, 20,0xFFFF);
	  }
	  /* USER CODE END StartGyroTask */
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
