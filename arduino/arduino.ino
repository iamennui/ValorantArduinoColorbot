#include <Mouse.h>

void setup() {
    Serial.begin(115200);
    Serial.setTimeout(1);
    Mouse.begin();
}

void loop() {
    if (Serial.available() > 0) {
        String command = Serial.readStringUntil('\n');
        command.trim();

        if (command[0] == 'M') {
            int commaIndex = command.indexOf(',');
            if (commaIndex > 1) {
                int deltaX = command.substring(1, commaIndex).toInt();
                int deltaY = command.substring(commaIndex + 1).toInt();
                Mouse.move(deltaX, deltaY);
            }
        } else if (command[0] == 'C') {
            Mouse.click();
        }
    }
}