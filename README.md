Bye Fusion
==========

This is a script to migrate your machines from greedy VmWare Fusion to 
slightly-less-greedy Oracle VirtualBox.

It works by converting VMX images to OVF, which can then be manually imported 
into VB. It takes care of the few known gotchas and low-level hacks to ensure 
the import process will not fail.

*Please fork and improve this script as you see fit, I'm always happy to get pull 
requests.*

Requirements 
-----------

- **Python 3.6**. I used this as an excuse to play with pathlib (3.4+) and 
f-strings (3.6+), but it should be fairly easy to make it run on 3.4+.

- **VmWare Fusion.app**. You can copy the trial version to `/Applications` 
and remove it right after running the script, there is no need to ever launch it.

VirtualBox is not actually required on the machine where you run this script.

Parameters
----------

`byefusion.py /path/to/machine.vmwarevm [/path/to/output/folder]`

Output folder defaults to `/tmp`.

Known Issues and Caveats
------------

- *About the script*
    
    - the script doesn't report progress very well. I just can't be arsed to find
out why the `subprocess` module is so bitchy. To check if it's running,
you can look in Activity Monitor for `ovftool`, which should be churning CPU
and disk resources; you will also get a `.tmp` file in the output directory,
which gets deleted once `ovftool` terminates.


- *About the overall process*
    
    - You might have to remove network cards in the VB import screen, if the image 
is recent, as newer Fusion versions use hardware that is not available in VB (cards
with FAST in the name). The script doesn't do that for you because you will likely 
want to tweak network config yourself in VB to work properly.

    - the way the whole process works, an image is copied twice: once as .ovf 
output, and again when VB imports it in its default VM folder. Make sure you
have enough space for that on your disk. After VB import succeeds, check that
it works and then you can delete the OVF version generated by this script.

    - VB import tries to guess the operating systems, but it often gets confused.
If you pick the wrong OS and bitness, import will succeed but the image won't 
boot. You should always review image settings after import to make sure they 
are correct.

    - You will have to manually uninstall VmWare Tools inside the image before
you can install the VB guest addons. This can be done before or after conversion.

    - In one case, the `ovftool` from VmWare flatly refused to handle an XP image
which had been with me for quite a few years. If that happens, you will have to
manually copy away the VMDK disk and recreate the machine from scratch with 
the disk attached. Before you do that, to improve your chances of success,
make sure your disk is monolithic (one file rather than several) and remove 
all snapshots if possible.

License
-------

**Copyright 2017 Giacomo Lacava**

Permission is hereby granted, free of charge, to any person obtaining a copy of 
this software and associated documentation files (the "Software"), to deal in 
the Software without restriction, including without limitation the rights to 
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies 
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

**The above copyright notice and this permission notice shall be included 
in all copies or substantial portions of the Software.**

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR 
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER 
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN 
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.