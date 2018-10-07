

function addr_to_decimal {
  Param($addr)
  $split = $addr.split(".")
  $split |
  % {
    $fin += [convert]::ToString($_, 2).PadLeft(8, '0')
  }
  return [convert]::ToInt64($fin, 2)
}


function decimal_to_addr {
  Param($decimal)
  $out = [convert]::ToString($decimal, 2).PadLeft(32, '0')
  $ret = $null
  for($x = 0; $x -lt 32; $x+=8) {
    $next = $x + 7
    $byte_string = $out[$x..$next] -join ''
    $byte = [convert]::ToInt64($byte_string, 2)
    $ret += [string]$byte + "."
  }
  $ret = $ret.Substring(0, $ret.length - 1)
  return $ret
}


function ping_range {
  Param($addr, $range)
  [string]$ping_to = $addr
  $up_hosts = @()
  for($x = 0; $x -lt $range; $x++) {
    $ret = ping $ping_to -n 1 -w 50
    <#write-host "Pinging host: " $ping_to#>
    if(( -not ($ret -match "unreachable")) -and  (-not ($ret -match "timed out"))){
      write-host "Host " $ping_to " UP"
      $up_hosts += $ping_to
    }
    $ping_to = (addr_to_decimal -addr $ping_to) + 1
    $ping_to = decimal_to_addr -decimal $ping_to
  }
  return $up_hosts
}


function parse_range {
  Param($range)
  
  $split_addr = @()
  if ($range -match "-") {
    $split_addr = $range.Split("-")
    $split_addr += "range"
  }
  elseif ($range -match "/") {
    $split_addr = $range.Split("/")
    $split_addr += "cidr"
  }
  else {
    Write-Host ("Improperly formatted range: " + $range)
  }
  return $split_addr
}


function main {
  $user_range = read-host "Enter IP range or CIDR notation >> "
  
  $parsed = parse_range -range $user_range
  if($parsed[-1] -eq "range") {
    $start = addr_to_decimal -addr $parsed[0]
    $end = addr_to_decimal -addr $parsed[1]
    $range = $end - $start
    $ping_to = decimal_to_addr -decimal $start
    $up_hosts = ping_range -addr $ping_to -range $range
  }
  elseif($parsed[-1] -eq "cidr") {
    $start = addr_to_decimal -addr $parsed[0]
    $start++
    $range = 1 -shl (32 - $parsed[1])
    $range--
    $ping_to = decimal_to_addr -decimal $start
    $up_hosts = ping_range -addr $ping_to -range $range
  }
  else {
    write-host "Invalid format"
    return
  }
  $up_hosts |
  % {
    write-host $_
  }
}

main

