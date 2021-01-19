from cmsis_svd.parser import SVDParser
from cmsis_svd.model import *
import re
import os


def read_template(name: str) -> str:
    f = open('./template/' + name, 'r')
    s = ""
    for line in f.readlines():
        s += line
    return s


def parse_description(desc: str) -> str:
    if (desc == None):
        return ''
    return re.sub('\\s+', ' ', desc.replace('\n', ' '))


def upper_hex(num: int) -> str:
    return hex(num).upper().replace('X', 'x')


def get_fields(reg: SVDRegister) -> str:
    buffer = ""
    for field in reg._fields:
        if field.bit_width == 1:
            buffer += BIT_TEMPLATE.format(name=field.name,
                                          offset=field.bit_offset,
                                          description=parse_description(field.description))
        else:
            buffer += FIELD_TEMPLATE.format(name=field.name,
                                            offset=field.bit_offset,
                                            description=parse_description(
                                                field.description),
                                            width=field.bit_width)
    return buffer


def get_register(reg: SVDRegister) -> str:
    buffer = REGISTER_TEMPLATE.format(description=parse_description(reg.description),
                                      address=upper_hex(reg.address_offset))

    buffer += get_fields(reg)

    return REG_STRUCT_TEMPLATE.format(name=reg.name,
                                      field=buffer,
                                      description=parse_description(reg.description))


def make_peripheral_header(periph: SVDPeripheral, destination_folder: str = 'chip') -> None:
    os.makedirs(f"./{destination_folder}", exist_ok=True)
    file = open(f"./{destination_folder}/{periph.name.lower()}.h", "w")
    register_fields = ""

    for reg in periph.registers:
        register_fields += get_register(reg)

    file.write(FILE_TEMPLATE.format(name=periph.name,
                                    description=parse_description(
                                        periph._description),
                                    address=upper_hex(periph._base_address),
                                    fields=register_fields))


REGISTER_TEMPLATE = read_template('register.h')
BIT_TEMPLATE = read_template('bit.h')
FIELD_TEMPLATE = read_template('field.h')
REG_STRUCT_TEMPLATE = read_template('reg_struct.h')
FILE_TEMPLATE = read_template('file.h')


parser = SVDParser.for_xml_file(path='./STM32L0x1.svd')

for periph in parser.get_device().peripherals:
    make_peripheral_header(periph, 'chip/STM32L0x1')
