# Some Scripts I've written for Animal Logic Academy (ALA)
## Maya
### Animation Curve Selector
A small tool that allows animators to isolate specific curves on the curve graph from selecting rig controls.

### FK/IK Switch
A tool written specifically for the two character rigs in the animated short *Alone*. It allows the user to switch between FK/IK mode for either rig, as long as the rig is selected. It also allows the user
to match poses from FK to IK and vice versa. 

### Wheel Rig
Another tool written for the rigs in *Alone*, this time specifically to automate the wheel animation progress. It uses the wheel's IK control to calculate speed and distance from frame to frame, then keys in the
appropriate position for each frame. The roll can be keyed to be on or off.

## Nuke
### Comp Builder
Designed by the 2023 comp team and their lead Ross Anderson, this tool brings in selected .exr sequences and light groups and fits them into a neat template ready to go.

It comes with two loading options: *shot* mode and *pass* mode. Shot mode will connect up all loaded passes along with an output area for publishing. Pass mode will simply load the selected passes and light groups.
There's also a button that allows the user to load in every pass and associated light group all at once (in either mode)
