function Is-Number {
    param(
        [string]$value
    )
    return $value -match "^[0-9]+$"
}

function Call-Tor-Script {
    param(
        [string]$value,
        [string]$type
    )
    if (Is-Number -value $value) {
        $torcmd = ".\updateClient\tor_" + $value + ".cmd"
        if ($type -eq "ip") {
            $torcmd = ".\updateClient\tor_ip_" + $value + ".cmd"
        }
        if ($type -eq "pos") {
            $torcmd = ".\updateClient\tor_pos_" + $value + ".cmd"
        }
        write-host "start $($type) $($value): $($torcmd)"
        cmd.exe /c "$($torcmd)"
    }
}

if ($args.count -gt 0) {
    $type = ""
    $startIdx = 0
    if ($args[0] -eq "-ip") {
        $type = "ip"
        $startIdx = 1;
    }
    if ($args[0] -eq "-pos") {
        $type = "pos"
        $startIdx = 1;
    }
    if ($args[0] -eq "-id") {
        $startIdx = 1
    }
    for ( $i = $startIdx; $i -lt $args.count; $i++ ) {
            Call-Tor-Script -value $args[$i] -type $type
    }
}