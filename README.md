# Yeelight Edge

An python script for MQTT-based control of local yeelight lamps.

## Setup

1. Clone the repo.
2. Fill in the missing information about the MQTT server in `yeelightConfig.yaml`.
3. Test the script by calling `python3 ./yeelightEdge.py`.
4. Adapt the path of `WorkingDirectory` and `ExecStart` in `yeelightEdge.service`.
4. Install the service to enable automatic running after a reboot by calling the script `sudo ./installService.sh`.

## Controlling yeelight lamps via MQTT

When the script is running it listens to the MQTT topic `home/lamp/yeelight/#`. A yeelight lamp can now be
controlled by sending a command to the topic `home/lamp/yeelight/<name_of_the_lamp>`. The name of the lamp must be the
last part of the topic. The message must be the command for the lamp. The following commands are possible:

| Command  | Description |
| --- | --- |
| `turnon` | Turns the lamp on. |
| `turnoff` | Turns the lamp off. |
| `toggle` | Toggles between on and off. |
| `flow <flow_name>` | Activates the flow with the name `flow_name`. Right now only `greenFlash` is a valid flow name. |