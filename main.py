from cmsis_svd.parser import SVDParser

parser = SVDParser.for_xml_file(
    path='./STM32L0x1.svd')

for periph in parser.get_device().peripherals:
    file = open(f"./chip/{periph.name.lower()}.h", "w")
    register_text = ""
    register_fields = ""

    for reg in periph.registers:
        register_text += f"    using {reg.name} = zol::register<uint32_t, address + {hex(reg.address_offset)}>;\n"
        reg_field = ""
        for field in reg.fields:
            if field.bit_width == 1:
                reg_field += f"        using {field.name} = zol::bit_rw<{reg.name}, {field.bit_offset}>\n"
            else:
                reg_field += f"        using {field.name} = zol::field_rw<{reg.name}, {field.bit_offset}, {field.bit_width}>\n"

        register_fields += f"""
    struct {reg.name.lower()} {{
{reg_field}
    private:
        {reg.name.lower()}() {{}}
    }};

    """

    file.write(f"""#pragma once

/// Note: This is automatically generated using a svd file
/// Warning: zol::bit_x and zol::field_x might have incorrect access restrictions, review might be necessary!

#include <bits.h>
#include <fields.h>
#include <register.h>

struct {periph.name} {{
    static constexpr zol::addr_t address = {hex(periph.base_address)};

{register_text}
{register_fields}
private:
    {periph.name}() {{}}
}};
""")
