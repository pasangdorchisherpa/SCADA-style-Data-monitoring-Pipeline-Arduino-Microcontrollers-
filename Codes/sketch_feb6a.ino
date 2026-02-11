#include <DHT.h>
#include <LiquidCrystal.h>

#define DHTPIN 2
#define DHTTYPE DHT11

#define BUZZER_PIN 9
#define TRIG_PIN 6
#define ECHO_PIN 7

// Parallel LCD pins: rs, en, d4, d5, d6, d7
LiquidCrystal lcd(12, 11, 5, 4, 3, 8);

const float TEMP_LOW = 18.0;
const float TEMP_HIGH = 30.0;
const int DIST_CLOSE_CM = 20;

DHT dht(DHTPIN, DHTTYPE);

unsigned long lastSensorMs = 0;
const unsigned long SENSOR_INTERVAL_MS = 2000;

long readDistanceCM() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  if (duration == 0) return -1;
  return duration / 58;
}

void beepPatternTempAlarm() {
  tone(BUZZER_PIN, 2200, 120);
  delay(160);
  tone(BUZZER_PIN, 2200, 120);
  delay(200);
}

void beepPatternDistanceAlarm() {
  tone(BUZZER_PIN, 2800, 80);
  delay(120);
  tone(BUZZER_PIN, 2800, 80);
  delay(120);
  tone(BUZZER_PIN, 2800, 80);
  delay(200);
}

void setup() {
  Serial.begin(9600);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  dht.begin();

  lcd.begin(16, 2);
  lcd.print("Starting...");
  delay(1200);
  lcd.clear();
}

void loop() {
  if (millis() - lastSensorMs >= SENSOR_INTERVAL_MS) {
    lastSensorMs = millis();

    float hum = dht.readHumidity();
    float temp = dht.readTemperature();
    int dist = (int)readDistanceCM();

    bool dhtOk = !(isnan(hum) || isnan(temp));
    bool distAlarm = (dist > 0 && dist <= DIST_CLOSE_CM);
    bool tempAlarm = dhtOk && (temp < TEMP_LOW || temp > TEMP_HIGH);

    // After reading: temp, hum, dist
    if (isnan(temp) || isnan(hum)) {
      Serial.println("ERROR");
    } else {
      Serial.print(millis());
      Serial.print(",");
      Serial.print(temp, 1);
      Serial.print(",");
      Serial.print(hum, 1);
      Serial.print(",");
      Serial.println(dist);  // use -1 if invalid
    }

    lcd.clear();
    lcd.setCursor(0, 0);

    if (dhtOk) {
      lcd.print("T:");
      lcd.print(temp, 1);
      lcd.print((char)223);
      lcd.print("C H:");
      lcd.print(hum, 0);
      lcd.print("%");
    } else {
      lcd.print("DHT11 ERROR");
    }

    lcd.setCursor(0, 1);
    lcd.print("Dist:");
    if (dist > 0) {
      lcd.print(dist);
      lcd.print("cm");
    } else {
      lcd.print("---");
    }

    if (distAlarm) beepPatternDistanceAlarm();
    else if (tempAlarm) beepPatternTempAlarm();
    else noTone(BUZZER_PIN);
  }
}
