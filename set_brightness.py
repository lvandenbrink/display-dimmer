import argparse
import screen_brightness_control as sbc

parser = argparse.ArgumentParser("set_brightness")
parser.add_argument("brightness", help="Value of brightness the monitor should be set.", type=int, nargs="?", default=42)
args = parser.parse_args()
brightness = args.brightness

displays = sbc.list_monitors_info()
for display in displays:
    print('=======================')
    # the manufacturer name plus the model
    print('Name:', display['name'])
    # the general model of the display
    print('Model:', display['model'])
    # the serial of the display
    print('Serial:', display['serial'])
    # the name of the brand of the display
    print('Manufacturer:', display['manufacturer'])
    # the 3 letter code corresponding to the brand name, EG: BNQ -> BenQ
    print('Manufacturer ID:', display['manufacturer_id'])
    # the index of that display FOR THE SPECIFIC METHOD THE DISPLAY USES
    print('Index:', display['index'])
    # the method this display can be addressed by
    print('Method:', display['method'])
    # the EDID string associated with that display
    print('EDID:', display['edid'])
    # The UID of the display
    print('UID:', display['uid'])

all_methods = sbc.get_methods()
for method_name, method_class in all_methods.items():
    print('Method:', method_name)
    print('Class:', method_class)
    print('Associated monitors:', sbc.list_monitors(method=method_name))
    

try:
    print(f"Brightness is {sbc.get_brightness()}")
    sbc.set_brightness(brightness)
    print(f"Brightness is set to {sbc.get_brightness()}")
except sbc.ScreenBrightnessError as error:
    print(error)