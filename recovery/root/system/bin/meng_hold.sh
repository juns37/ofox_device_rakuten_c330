#!/system/bin/sh
[ "$(getprop meng.rom.layout)" = dynamic ] || exit 0
L=/tmp/meng_hold.log
i=0
while [ $i -lt 600 ]; do
	grep -q " /data " /proc/mounts && break
	sleep 0.05
	i=$((i+1))
done
mkdir -p /mnt/.mhold
mount --bind /data /mnt/.mhold && echo "hold $(date +%T)" >> $L
i=0
while [ $i -lt 1200 ]; do
	[ "$(getprop twrp.all.users.decrypted)" = "true" ] && break
	sleep 0.1
	i=$((i+1))
done
umount /mnt/.mhold && echo "release $(date +%T) decrypted=$(getprop twrp.all.users.decrypted)" >> $L
exit 0
