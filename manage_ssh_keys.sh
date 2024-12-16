#!/bin/bash

# Función para mover las claves y agregar al archivo authorized_keys
manage_ssh_keys() {
    local user=$1
    local source_dir="/mnt/smb/ssh/$user/.ssh"
    local dest_dir="/home/$user/.ssh"
    local authorized_keys="$dest_dir/authorized_keys"
    
    # Verificar si el directorio de origen existe
    if [ ! -d "$source_dir" ]; then
        echo "El directorio de origen $source_dir no existe. No se pueden mover las claves para $user."
        return 1
    fi

    # Crear el directorio de destino .ssh si no existe
    if [ ! -d "$dest_dir" ]; then
        echo "El directorio $dest_dir no existe. Creando..."
        mkdir -p "$dest_dir"
        chmod 700 "$dest_dir"  # Permisos adecuados para .ssh
    fi

    # Mover las claves SSH al directorio destino
    echo "Moviendo las claves de $user desde $source_dir a $dest_dir..."
    mv "$source_dir"/* "$dest_dir/"
    
    # Asegurar que las claves privadas y públicas tengan los permisos correctos
    chmod 600 "$dest_dir"/*_rsa      # Clave privada
    chmod 644 "$dest_dir"/*.pub       # Clave pública

    # Asegurar que el archivo authorized_keys existe
    if [ ! -f "$authorized_keys" ]; then
        echo "El archivo authorized_keys no existe. Creando uno nuevo..."
        touch "$authorized_keys"
        chmod 600 "$authorized_keys"  # El archivo debe tener permisos 600
    fi

    # Agregar las claves públicas al archivo authorized_keys si no están presentes
    for pub_key in "$dest_dir"/*.pub; do
        # Verificar si la clave ya está en authorized_keys
        if ! grep -q "$(cat "$pub_key")" "$authorized_keys"; then
            echo "Agregando la clave pública $(basename "$pub_key") de $user al archivo authorized_keys..."
            cat "$pub_key" >> "$authorized_keys"
        else
            echo "La clave pública $(basename "$pub_key") de $user ya está en authorized_keys. No es necesario agregarla."
        fi
    done

    # Cambiar el propietario de .ssh y authorized_keys al usuario correspondiente
    echo "Estableciendo el propietario correcto para el directorio y las claves..."
    chown -R "$user:$user" "$dest_dir"
    
    echo "Las claves de $user han sido gestionadas correctamente."
}

# Mover y gestionar las claves de los usuarios 'john' y 'alice'
manage_ssh_keys "john"
#manage_ssh_keys "alice"
