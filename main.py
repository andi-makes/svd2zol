from cmsis_svd.parser import SVDParser
import re


def parse_description(desc: str) -> str:
    if (desc == None):
        return ''
    return re.sub('\\s+', ' ', desc.replace('\n', ' '))


parser = SVDParser.for_xml_file(
    path='./STM32L0x1.svd')

for periph in parser.get_device().peripherals:
    file = open(f"./chip/{periph.name.lower()}.h", "w")
    register_text = ""
    register_fields = ""

    for reg in periph.registers:
        register_text += f"""    /// @brief {parse_description(reg.description)}
    using {reg.name} = zol::reg<uint32_t, address + {hex(reg.address_offset)}>;\n"""
        reg_field = f"""        /// @brief {parse_description(reg.description)}
        using reg = zol::reg<uint32_t, address + {hex(reg.address_offset)}>;\n"""
        for field in reg.fields:
            if field.bit_width == 1:
                reg_field += f"""        /// @brief {parse_description(field.description)}
        using {field.name} = zol::bit_rw<reg, {field.bit_offset}>\n"""
            else:
                reg_field += f"""        /// @brief {parse_description(field.description)}
        using {field.name} = zol::field_rw<reg, {field.bit_offset}, {field.bit_width}>\n"""

        register_fields += f"""    /// @brief {parse_description(reg.description)}
    struct {reg.name} {{
{reg_field}
    private:
        {reg.name}() {{}}
    }};

"""

    file.write(f"""#pragma once

/// Note: This is automatically generated using a svd file
/// Warning: zol::bit_x and zol::field_x might have incorrect access restrictions, review might be necessary!

#include <bits.h>
#include <fields.h>
#include <register.h>

/// @brief {parse_description(periph._description)}
struct {periph.name} {{
    static constexpr zol::addr_t address = {hex(periph.base_address)};

{register_fields}private:
    {periph.name}() {{}}
}};
""")
