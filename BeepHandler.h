
#define BEEPS_IN_PATTERN 3

extern int buzzerPin;

class BeepHandler {
  int curBeepMs;
  int curQuietMs;
  unsigned long startTime;

private:
  void initiateBeeping(unsigned long currentMillis) {
    Serial.println("init beeping");
    curBeepMs = 500;
    curQuietMs = 2000;
    startTime = currentMillis;
  }

public:

  BeepHandler() {
    curBeepMs = 0;
  }

  void reset() {
    digitalWrite(buzzerPin, LOW);
    curBeepMs = 0;
  }

  void startOrContinue(unsigned long currentMillis) {
    if(curBeepMs == 0) {
      initiateBeeping(currentMillis);
      digitalWrite(buzzerPin, HIGH);
    }
  }

  void handle(unsigned long currentMillis) {
    if(curBeepMs == 0) {
      return;
    }
    
    unsigned long delta = currentMillis - startTime;
    if((curBeepMs + curQuietMs)*BEEPS_IN_PATTERN < delta) {
      if(curQuietMs > 500) {
        curBeepMs *= 2;
        curQuietMs /= 2;
      }
      startTime = currentMillis;
    }

    //Serial.println("delta = " + String(delta) + " cur=" + String(currentMillis) + " start=" + String(startTime));
    delta = delta % (curBeepMs + curQuietMs);
    //Serial.println("delta = " + String(delta) + " beep=" + String(curBeepMs) + " quiet=" + String(curQuietMs));
    if(delta < curBeepMs)
      digitalWrite(buzzerPin, HIGH);
    else // (delta < curBeepMs + curQuietMs)
      digitalWrite(buzzerPin, LOW);
  }
};

