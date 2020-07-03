#!/bin/bash

d=$( date +%Y%m%d )

for m in \
    boot \
    system \
    userdata \
    thalmic \
    config \
    persist \
    oem \
    keystore \
    keymasterbak \
    keymaster \
    cmnlibbak \
    cmnlib \
    devinfo \
    recovery \
    cache \
    sec \
    fsg \
    DDR \
    splash \
    ssd \
    fsc \
    misc \
    modemst2 \
    modemst1 \
    pad \
    tzbak \
    tz \
    rpmbak \
    rpm \
    abootbak \
    aboot \
    sbl1bak \
    sbl1 \
    modem 
do
    if [ ! -e "backup/${m}.${d}.img" ]
    then
        FN=backup/${m}.${d}.img
        echo "${m} -> ${FN}"

        sudo python edl.py r ${m} ${FN} --loader=Loaders/009600E10029001B_cc3153a80293939b_FHPRG.bin 
        if [ $? -ne 0 ]
        then
            echo "FAIL"
            break
        fi

    fi
done




# Partition table:
#
#modem:               Offset 0x0000000004000000, Length 0x0000000004000000, Flags 0x00000010, UUID 7021e069-200f-d567-4d9d-208b5ce91c51, Type EFI_BASIC_DATA
#sbl1:                Offset 0x0000000008000000, Length 0x0000000000080000, Flags 0x00000000, UUID e0ca1ec6-5c24-c083-ff4a-5ee595c595da, Type 0xdea0ba2c
#sbl1bak:             Offset 0x0000000008080000, Length 0x0000000000080000, Flags 0x00000000, UUID fbabc46f-3911-b32a-d052-0ad870ce1a90, Type 0xdea0ba2c
#aboot:               Offset 0x0000000008100000, Length 0x0000000000100000, Flags 0x00000000, UUID 3e4e3b1c-b846-970c-da5b-f27f61c05cee, Type 0x400ffdcd
#abootbak:            Offset 0x0000000008200000, Length 0x0000000000100000, Flags 0x00000000, UUID f339ae81-f064-48e8-cd70-b510cba7e239, Type 0x400ffdcd
#rpm:                 Offset 0x0000000008300000, Length 0x0000000000080000, Flags 0x00000000, UUID 5d191f2c-911d-e94f-2422-d7fa4bb3518b, Type 0x98df793
#rpmbak:              Offset 0x0000000008380000, Length 0x0000000000080000, Flags 0x00000000, UUID c70cd0ee-44c8-dafb-11e4-6f8e06d0a3f8, Type 0x98df793
#tz:                  Offset 0x0000000008400000, Length 0x00000000000c0000, Flags 0x00000000, UUID 887da1e2-fbec-7587-563d-d7f0ddaefd81, Type 0xa053aa7f
#tzbak:               Offset 0x00000000084c0000, Length 0x00000000000c0000, Flags 0x00000000, UUID 0cb0036a-a5ee-6ac4-119d-9a50a10233b9, Type 0xa053aa7f
#pad:                 Offset 0x0000000008580000, Length 0x0000000000100000, Flags 0x00000000, UUID 5db72038-78df-095e-9e0b-961eb9d39c26, Type EFI_BASIC_DATA
#modemst1:            Offset 0x0000000008680000, Length 0x0000000000180000, Flags 0x00000000, UUID 42b831c7-0a42-4902-0e9d-7259baa6347c, Type 0xebbeadaf
#modemst2:            Offset 0x0000000008800000, Length 0x0000000000180000, Flags 0x00000000, UUID 9dba3f77-c8c2-6059-d93f-ad9a87a5a1b5, Type 0xa288b1f
#misc:                Offset 0x0000000008980000, Length 0x0000000000100000, Flags 0x00000000, UUID afde5123-fd3a-37af-dabc-73bfc996be5d, Type 0x82acc91f
#fsc:                 Offset 0x0000000008a80000, Length 0x0000000000000400, Flags 0x00000000, UUID 426184ee-8f0e-b975-5853-7c851f2d5692, Type 0x57b90a16
#ssd:                 Offset 0x0000000008a80400, Length 0x0000000000002000, Flags 0x00000000, UUID 3572f760-7d54-4d46-56ec-ea25fd83231b, Type 0x2c86e742
#splash:              Offset 0x0000000008a82400, Length 0x0000000000a00000, Flags 0x00000000, UUID b8a7afbc-19c8-426f-9434-4755a34a96ed, Type 0x20117f86
#DDR:                 Offset 0x000000000c000000, Length 0x0000000000008000, Flags 0x00000010, UUID e0f24983-a175-8009-5a5a-eb4c3cb3eb70, Type 0x20a0c19c
#fsg:                 Offset 0x000000000c008000, Length 0x0000000000180000, Flags 0x00000010, UUID 0c758831-f703-6c2d-ee3c-c47c8f36bf94, Type 0x638ff8e2
#sec:                 Offset 0x000000000c188000, Length 0x0000000000004000, Flags 0x00000010, UUID 3159e6ed-4a51-a248-34d7-586a841e9c99, Type 0x303e6ac3
#boot:                Offset 0x000000000c18c000, Length 0x0000000002000000, Flags 0x00000010, UUID e5d69c78-f387-5235-e30a-437303f4b053, Type 0x20117f86
#system:              Offset 0x000000000e18c000, Length 0x000000004cccd000, Flags 0x00000010, UUID d440ea78-84ab-5a3e-1ce1-6efdb883ab49, Type 0x97d7b011
#persist:             Offset 0x000000005ae59000, Length 0x0000000001400000, Flags 0x00000010, UUID 1d23fe45-d88d-3cdf-4b00-22053f71935f, Type 0x6c95e238
#cache:               Offset 0x000000005c259000, Length 0x0000000010000000, Flags 0x00000010, UUID 32274523-2e8a-2416-7b1a-cb44df9db824, Type 0x5594c694
#recovery:            Offset 0x000000006c259000, Length 0x0000000002000000, Flags 0x00000010, UUID 3717eae8-3bf8-3bd3-b6fc-de39a22855fa, Type 0x9d72d4e4
#devinfo:             Offset 0x000000006e259000, Length 0x0000000000100000, Flags 0x00000010, UUID efce75c3-9b85-af70-52fc-b692970acf8d, Type 0x1b81e7e6
#cmnlib:              Offset 0x000000006e359000, Length 0x0000000000040000, Flags 0x00000010, UUID b74bda97-a429-42af-d76e-dc5e9f4edf96, Type 0x73471795
#cmnlibbak:           Offset 0x000000006e399000, Length 0x0000000000040000, Flags 0x00000010, UUID dddd67e5-827b-88ea-24e3-d311d568a5cb, Type 0x73471795
#keymaster:           Offset 0x000000006e3d9000, Length 0x0000000000040000, Flags 0x00000010, UUID e21e33a8-f334-840d-3c65-6dac83eade75, Type 0xe8b7cf6e
#keymasterbak:        Offset 0x000000006e419000, Length 0x0000000000040000, Flags 0x00000010, UUID bfc88624-0cb2-29c4-87b2-25d23a6d97fe, Type 0xe8b7cf6e
#keystore:            Offset 0x0000000070000000, Length 0x0000000000080000, Flags 0x00000000, UUID afac0ba6-f34b-bdbe-29d2-b0809c4d0bcb, Type 0xde7d4029
#oem:                 Offset 0x0000000070080000, Length 0x0000000004000000, Flags 0x00000000, UUID ae7c10c7-670b-f743-395d-f5c473ca5b1b, Type 0x7db6ac55
#config:              Offset 0x0000000074080000, Length 0x0000000000080000, Flags 0x00000000, UUID 6ff9a927-b31d-fa72-1f67-244c45fc6ed9, Type 0x91b72d4d
#userdata:            Offset 0x0000000074100000, Length 0x0000000063ec6000, Flags 0x00000000, UUID 1d17e18c-ecfb-c246-f5ed-9610a4d1148d, Type 0x1b81e7e6
#thalmic:             Offset 0x00000000d8000000, Length 0x0000000010ffbe00, Flags 0x00000010, UUID 3276bc10-e948-9a2a-bf55-06a7102790da, Type 0xd5786476
