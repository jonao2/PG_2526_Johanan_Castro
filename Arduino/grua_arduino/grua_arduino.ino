#include <AccelStepper.h>

// ----------------------------------------------------
// 1. ASIGNACIÓN DE PINES
// ----------------------------------------------------
// Pines Joysticks
#define JOY_X A0 // Carro
#define JOY_Y A1 // Elevación
#define JOY_Z A2 // Giro

// Pines Driver TB6612FNG (Motor A - Carro)
#define AIN1 2
#define AIN2 4
#define PWMA 3

// Pines Driver TB6612FNG (Motor B - Elevación)
#define BIN1 7
#define BIN2 8
#define PWMB 5

// Pines Driver DRV8825 (Motor a pasos Nema 17 - Giro)
#define STEP_PIN 9
#define DIR_PIN 10

// ----------------------------------------------------
// 2. CONFIGURACIÓN DE LIBRERÍAS Y VARIABLES
// ----------------------------------------------------
// Configurar AccelStepper en modo DRIVER (1 pin de paso, 1 pin de dirección)
AccelStepper stepper(AccelStepper::DRIVER, STEP_PIN, DIR_PIN);

// Variables de estado para el Control Web (Valores de -1 a 1)
int webCarro = 0;   
int webElev = 0;    
int webGiro = 0;    

// Variables para el Timeout de Seguridad
unsigned long lastWebCommandTime = 0;
const unsigned long WEB_TIMEOUT = 1000; // Si pasa 1 seg sin comandos web, se detiene la aportación web

void setup() {
  // Configuración de Comunicación Serial (ESP32 TX -> Nano RX D0)
  Serial.begin(9600);
  
  // Configuración de pines de salida para TB6612FNG
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(PWMA, OUTPUT);
  
  pinMode(BIN1, OUTPUT);
  pinMode(BIN2, OUTPUT);
  pinMode(PWMB, OUTPUT);

  // Configuración de Motor a Pasos
  stepper.setMaxSpeed(1000); // Ajustar según los microsteps del DRV8825
  stepper.setAcceleration(500);
}

// ----------------------------------------------------
// 3. LÓGICA DE CONTROL WEB (PARSER UART)
// ----------------------------------------------------
void processWebCommand() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    lastWebCommandTime = millis();
    
    // Resetear estados antes de aplicar el nuevo comando
    webCarro = 0;
    webElev = 0;
    webGiro = 0;
    
    switch(cmd) {
      case 'F': webCarro = 1; break;  // Adelante (Carro)
      case 'B': webCarro = -1; break; // Atrás (Carro)
      case 'U': webElev = 1; break;   // Subir (Elevación)
      case 'D': webElev = -1; break;  // Bajar (Elevación)
      case 'L': webGiro = 1; break;   // Giro Izquierda
      case 'R': webGiro = -1; break;  // Giro Derecha
      case 'S': /* Todo en 0 */ break; // Parar
    }
  }
  
  // Timeout de Seguridad
  if (millis() - lastWebCommandTime > WEB_TIMEOUT) {
    webCarro = 0;
    webElev = 0;
    webGiro = 0;
  }
}

// ----------------------------------------------------
// 4. FUNCIONES AUXILIARES
// ----------------------------------------------------
// Mapeo analógico con zona muerta para evitar derivas del joystick
int mapWithDeadband(int val, int center, int deadband) {
  if (abs(val - center) < deadband) return 0;
  if (val > center) return map(val, center + deadband, 1023, 0, 255);
  return map(val, 0, center - deadband, -255, 0);
}

// Función para controlar motores con el TB6612FNG
void controlDC(int in1, int in2, int pwm, int speed) {
  if (speed > 0) {
    digitalWrite(in1, HIGH);
    digitalWrite(in2, LOW);
    analogWrite(pwm, speed);
  } else if (speed < 0) {
    digitalWrite(in1, LOW);
    digitalWrite(in2, HIGH);
    analogWrite(pwm, -speed);
  } else {
    digitalWrite(in1, LOW);
    digitalWrite(in2, LOW);
    analogWrite(pwm, 0);
  }
}

// ----------------------------------------------------
// 5. BUCLE PRINCIPAL (CONTROL MIXTO)
// ----------------------------------------------------
void loop() {
  // 1. Leer peticiones web
  processWebCommand();
  
  // 2. Leer Joysticks (Valores de 0 a 1023, centrado en ~512)
  int joyX = analogRead(JOY_X);
  int joyY = analogRead(JOY_Y);
  int joyZ = analogRead(JOY_Z);
  
  // Mapear intenciones del joystick de -255 a 255
  int joyCarro = mapWithDeadband(joyX, 512, 50);
  int joyElev = mapWithDeadband(joyY, 512, 50);
  int joyGiro = mapWithDeadband(joyZ, 512, 50);
  
  // 3. Sumar Intenciones (Joystick + Web)
  // La intención web aporta velocidad máxima (255) al sumarse
  int finalCarro = constrain(joyCarro + (webCarro * 255), -255, 255);
  int finalElev = constrain(joyElev + (webElev * 255), -255, 255);
  int finalGiro = constrain(joyGiro + (webGiro * 255), -255, 255); 
  
  // 4. Accionar Motores DC
  controlDC(AIN1, AIN2, PWMA, finalCarro);
  controlDC(BIN1, BIN2, PWMB, finalElev);
  
  // 5. Accionar Stepper Motor (Ejecución No Bloqueante)
  if (abs(finalGiro) > 10) {
    float speed = map(finalGiro, -255, 255, -1000, 1000);
    stepper.setSpeed(speed);
    stepper.runSpeed();
  } else {
    stepper.setSpeed(0);
    stepper.stop();
  }
}
