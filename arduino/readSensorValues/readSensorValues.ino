// Mux for sensors:
#define PIN_A 2
#define PIN_B 3
#define PIN_C 4
// for debugging purpose:
#define Log(value)  Serial.println("The value of " + String(#value)  + " is: " + String(value))

// to buffer the read sensor data
const size_t buff_size = 8;
int sensor_buff[buff_size] = {};


// arduino initialisation here
void setup() {
  Serial.begin(19200);
  // Mux for sensors:
  pinMode(PIN_A, OUTPUT);
  pinMode(PIN_B, OUTPUT);
  pinMode(PIN_C, OUTPUT);
}


// addressing pin p (0 - 7)
void addressing_mux(int p) {
  /* 
   * on arduino a integer value has 16bit
   * with a bitwise AND: &, plus the according 16bit Hex mask
   * we can address the mux pins easily:
   */ 
  digitalWrite(PIN_A, p & 0x01);
  digitalWrite(PIN_B, p & 0x02);
  digitalWrite(PIN_C, p & 0x04);
}


/* 
 * switching through 0 to x pin on Mux,
 * delay time in ms between switching,
 * so each pin will be connected to A0 and saved in bufer
 */
void switch_through_mux(int x, int delay_time, int* buffer) {
    for(int j = 0; j <= x; j++) {
      addressing_mux(j);
      delay(delay_time);
      buffer[j] = analogRead(A0);
    }
}

/* 
 * print values from buffer as csv,
 * send data as csv over serial connection: 
 */
void my_print(int* buffer, size_t buff_size){
  // seperate values by comma
  for (int i = 0; i < buff_size-1; i++) {
    Serial.print(buffer[i]);
    Serial.print(",");
  }
  // for the last value we need to break line
  Serial.println(buffer[buff_size-1]);
  // wait till all data is written:
  Serial.flush();
}



// send 0-7 --> address pin 0-7 on Mux
void read_serial_command() {
  if (Serial.available() > 0) {
    char received_byte = Serial.read();
    switch (received_byte) {
      case '0':
      case '1':
      case '2':
      case '3':
      case '4':
      case '5':
      case '6':
      case '7':
        addressing_mux(received_byte);
        break;
      default:
        Serial.println("No command linkend to: " + String(received_byte));
        break;
    }
  }
}

/*
 * continously read sensor values and send them over serial connection
 */
void loop() {
  switch_through_mux(buff_size, 20, sensor_buff);
  my_print(sensor_buff, buff_size);
}
