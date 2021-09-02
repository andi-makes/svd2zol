use svd_parser as svd;

use std::fs::File;
use std::io::Read;

fn get_fields(reg: &svd::Register) -> String {
    let mut buffer = String::new();
    for field in reg.fields.as_ref().unwrap() {
        if field.bit_range.width == 1 {
            buffer += &format!(
                r#"/// @brief {}
using {} = zol::bit_rw<reg, {}>;"#,
                field.description.as_ref().unwrap(),
                field.name,
                field.bit_range.offset
            );
        } else {
            buffer += &format!(
                r#"/// @brief {}
using {} = zol::field_rw<reg, {}, {}>;"#,
                field.description.as_ref().unwrap(),
                field.name,
                field.bit_range.offset,
                field.bit_range.width
            );
        }
    }

    buffer
}

fn get_register(reg: &svd::Register) -> String {
    let mut buffer = format!(
        r#"/// @brief {}
using reg = zol::reg<uint32_t, address + {}"#,
        reg.description.as_ref().unwrap(),
        reg.address_offset
    );

    buffer += &get_fields(reg);

    return format!(
        r#"/// @brief {}
struct {name} {{
    {field}
    {name}() = delete;
"#,
        reg.description.as_ref().unwrap(),
        name = reg.name,
        field = buffer
    );
}

fn make_peripheral_header(
    periph: svd::Peripheral,
    destination_folder: &str,
) -> std::io::Result<()> {
    std::fs::create_dir_all(format!("./{}", destination_folder))?;

    let mut register_fields = String::new();
    match periph.registers {
        Some(registers) => {
            for regcluster in registers {
                match regcluster {
                    svd::RegisterCluster::Register(reg) => register_fields += &get_register(&reg),
                    svd::RegisterCluster::Cluster(_) => todo!(),
                }
            }
        }
        None => (),
    }

    let contents = format!(
        r#"#pragma once
/// Note: This is automatically generated using a svd file
/// Warning: zol::bit_x and zol::field_x might have incorrect access restrictions, review might be necessary!

#include <bits.h>
#include <fields.h>
#include <register.h>

/// @brief {description}
struct {name} {{
    static constexpr zol::addr_t address = {address};

{fields}
{name}()=delete;
}};"#,
        description = "",
        name = periph.name,
        address = periph.base_address,
        fields = register_fields
    );

    std::fs::write(
        format!("./{}/{}.h", destination_folder, periph.name.to_lowercase()),
        contents,
    )?;

    Ok(())
}

fn main() -> std::io::Result<()> {
    let xml = &mut String::new();
    File::open("STM32L0x1.svd").unwrap().read_to_string(xml)?;
    let parser = svd::parse(xml).unwrap();

    for periph in parser.peripherals {
        make_peripheral_header(periph, &format!("chip/{}", parser.name))?;
    }

    Ok(())
}
