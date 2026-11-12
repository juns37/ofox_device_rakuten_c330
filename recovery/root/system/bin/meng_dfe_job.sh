#!/system/bin/sh
LOGF=/tmp/recovery.log
PLOG=/persist/OFRP/meng_auto.log
J=/persist/OFRP/meng_job
T=/tmp/meng_job
log() {
	echo "I:meng_dfe_job: $*" >> $LOGF
	echo "$(date '+%m-%d %H:%M:%S') job $*" >> $PLOG 2>/dev/null
}
final() {
	[ -d $T ] || return 0
	if [ -f $T/reboot ]; then
		rm -rf $T
		log "reboot system dalam 3 detik"
		sync
		sleep 3
		setprop sys.powerctl reboot
		sleep 5
		reboot
	fi
	rm -rf $T
	log "selesai"
}
case "$1" in
	pre)
		rm -rf $T
		cp -r $J $T
		rm -rf $J
		sync
		log "mulai: $(ls $T | tr '\n' ' ')"
		;;
	post)
		if [ -f $T/zip ] && [ "$2" != "0" ]; then
			log "DFE gagal (status '$2'), wipe & reboot dibatalkan"
			W=0; [ -f $T/wipe_data ] && W=1
			rm -rf $T
			if [ "$W" = "1" ]; then
				log "wipe data dibatalkan dengan reboot recovery"
				cp $LOGF /persist/OFRP/meng_dfe_fail.log 2>/dev/null
				sync
				setprop sys.powerctl reboot,recovery
				sleep 5
				reboot recovery
			fi
			exit 1
		fi
		[ -f $T/wipe_data ] || final
		;;
	final)
		final
		;;
esac
exit 0
