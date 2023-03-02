from building import *
import rtconfig

cwd     = GetCurrentDir()

src     = []
CPPPATH = [cwd]

LIBS    = []
LIBPATH = []

if GetDepend('SOC_FH8620'):
    LIBS = ['wlan-wiced_gcc_fh8620']
    LIBPATH = [cwd + '/fh8620']
    
elif GetDepend('BOARD_X1000_REALBOARD'):
    LIBPATH = [cwd + '/x1000']

    if GetDepend('RT_USING_HARD_FLOAT'):
        LIBS = ['wlan-wiced_gcc_x1000_fpu.a']        
    else:
        LIBS = ['wlan-wiced_gcc_x1000.a']

elif GetDepend('SOC_STM32L475VE'):
    LIBPATH = [cwd + '/stm32l4']

    if rtconfig.CROSS_TOOL == 'gcc':
        LIBS = ['wifi_6181_0.2.6_armcm4_gcc']    
    elif rtconfig.CROSS_TOOL == 'keil':
        LIBS = ['libwifi_6181_0.2.6_armcm4_keil']
    else:
        LIBS = ['libwifi_6181_0.2.6_armcm4_iar']

group = DefineGroup('wlan-wiced', src, depend = ['PKG_USING_WLAN_WICED', 'RT_USING_LWIP'], CPPPATH = CPPPATH, LIBS = LIBS, LIBPATH = LIBPATH)

Return('group')
