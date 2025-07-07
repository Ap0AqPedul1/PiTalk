Jika Terminal maka Setup Audionya

aplay -l

nano ~/.asoundrc
defaults.pcm.card 2
defaults.ctl.card 2

test dengan ini
speaker-test -t wav