#!/system/bin/sh
LOGF=/tmp/recovery.log
PLOG=/persist/OFRP/meng_auto.log
J=/persist/OFRP/meng_job
log() {
	echo "I:meng_postflash: $*" >> $LOGF
	mkdir -p /persist/OFRP 2>/dev/null
	echo "$(date '+%m-%d %H:%M:%S') $*" >> $PLOG 2>/dev/null
}
REC=$1; DFE=$2; SYS=$3; ST=$4
[ "$DFE" = "1" ] || DFE=
[ "$REC" = "1" ] || [ -n "$DFE" ] || exit 0
log "rec='$REC' dfe='$DFE' reboot_sys='$SYS' status='$ST'"
if [ "$ST" != "0" ]; then
	log "flash gagal, auto reboot dibatalkan"
	exit 0
fi
rm -rf $J
if [ -n "$DFE" ]; then
	if mkdir -p $J; then
		touch $J/dfe $J/zip
		[ "$SYS" = "1" ] && touch $J/reboot
		touch $J/go
		log "job: $(ls $J | tr '\n' ' ')"
	else
		log "E: gagal membuat $J"
	fi
fi
log "reboot recovery dalam 3 detik"
sync
sleep 3
setprop sys.powerctl reboot,recovery
sleep 5
reboot recovery
exit 0
