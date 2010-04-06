#!/bin/bash

#play a open sound
paplay ~/Audio/Sounds/ui_pipboy_light_on.wav

#change Pidgin status
purple-remote 'setstatus?status=available&message=I am here...'
