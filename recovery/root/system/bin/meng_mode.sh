#!/system/bin/sh
B=/dev/block/bootdevice/by-name/system
[ -e $B ] || B=/dev/block/platform/soc/7824900.sdhci/by-name/system
m1=$(dd if=$B bs=4096 skip=1 count=1 2>/dev/null | head -c 4)
m0=$(dd if=$B bs=4096 count=1 2>/dev/null | head -c 4)
E=/system/etc
if [ "$m1" = "gDla" ] || [ "$m0" = "gDla" ]; then
	cp -f $E/recovery.fstab.dyn $E/recovery.fstab
	cp -f $E/twrp.flags.dyn $E/twrp.flags
	resetprop ro.boot.dynamic_partitions true
	resetprop ro.boot.dynamic_partitions_retrofit true
	resetprop ro.crypto.volume.options aes-256-xts:aes-256-cts:v2
	setprop meng.rom.layout dynamic
else
	resetprop ro.boot.dynamic_partitions false
	resetprop --delete ro.boot.dynamic_partitions_retrofit
	setprop meng.rom.layout legacy
fi
exit 0
