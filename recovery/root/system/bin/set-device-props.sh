#!/system/bin/sh
for i in "" odm. product. system. system_ext. vendor.; do
	resetprop "ro.product.${i}device" "c330ae"
	resetprop "ro.product.${i}model" "Rakuten Mini"
	resetprop "ro.product.${i}brand" "Rakuten"
	resetprop "ro.product.${i}manufacturer" "TINNO"
done
resetprop "ro.build.product" "c330ae"
exit 0
