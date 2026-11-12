$(call inherit-product, $(SRC_TARGET_DIR)/product/core_64_bit.mk)
$(call inherit-product, $(SRC_TARGET_DIR)/product/base.mk)
$(call inherit-product, vendor/twrp/config/common.mk)
$(call inherit-product, device/rakuten/c330ae/device.mk)

PRODUCT_DEVICE := c330ae
PRODUCT_NAME := twrp_c330ae
PRODUCT_BRAND := Rakuten
PRODUCT_MODEL := Rakuten Mini
PRODUCT_MANUFACTURER := TINNO
PRODUCT_RELEASE_NAME := Rakuten Mini
