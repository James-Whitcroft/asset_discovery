
<# convert an ip address into a decimal #>
function addr_to_decimal {
  Param($addr)
  $split = $addr.split(".")
  $split |
  % {
    <# convert current octet to string #>
    $fin += [convert]::ToString($_, 2).PadLeft(8, '0')
  }
  return [convert]::ToInt64($fin, 2) <# return decimal value of entire ip #>
}

<# convert a decimal into an ip address #>
function decimal_to_addr {
  Param($decimal)
  <# convert decimal into binary string pad left with zero until 32 bits #>
  $out = [convert]::ToString($decimal, 2).PadLeft(32, '0')
  $ret = $null
  for($x = 0; $x -lt 32; $x+=8) {
    $next = $x + 7
    $byte_string = $out[$x..$next] -join '' <# substring 8 bits #>
    $byte = [convert]::ToInt64($byte_string, 2) <# convert substring into decimal #>
    $ret += [string]$byte + "."
  }
  $ret = $ret.Substring(0, $ret.length - 1)
  return $ret
}

<# ping from decimal representation of ip addr to addr + range #>
function ping_range {
  Param($addr, $range, $quiet)
  [string]$ping_to = $addr
  $up_hosts = @{} <# create an empty hashtable #>
  for($x = 0; $x -lt $range; $x++) {
    if( -not $quiet) { write-host "Pinging " $ping_to }
    $ret = ping $ping_to -n 1 -w 100 <# run ping command #>
    if(( -not ($ret -match "unreachable")) -and  (-not ($ret -match "timed out"))){
      if( -not $quiet) { write-host "Host " $ping_to " UP" }
      $test = $ret.split(" ").where{ $_ -match "TTL="}
      $test = $test.split("=")
      $test = $test[-1]
      <# checkin TTL for OS guess 
       # could be more accutate with hop count
       # but it is faster this way
       #>
      if([convert]::ToInt64($test, 10) -gt 100) {
        if( -not $quiet) { write-host "Likely Windows OS" }
        $os = "Windows"
      } else {
        if( -not $quiet) { write-host "Likely *nix OS" }
        $os = "Linux"
      }
      
      $up_hosts[$ping_to] = $os <# found a host, append to return array #>
    }
    <# convert ip to decimal and increment by one #>
    $ping_to = (addr_to_decimal -addr $ping_to) + 1
    <# convert decimal back to ip #>
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
    return -1
  }
  return $split_addr
}


function main_ping_sweep {
  $user_range = read-host "Enter IP range or CIDR notation >> "
  
  $parsed = parse_range -range $user_range <# parses input and labels it as range or cidr notation #>
  
  if($parsed -eq -1){main}
  if($parsed[-1] -eq "range") {
    $start = addr_to_decimal -addr $parsed[0] <# convert start ip to decimal #>
    $end = addr_to_decimal -addr $parsed[1] <# convert stop ip to decimal #>
    $range = ($end - $start) + 1 <# find delta, inclusive #>
    $ping_to = decimal_to_addr -decimal $start
    $up_hosts = ping_range -addr $ping_to -range $range -quiet 0
  }
  elseif($parsed[-1] -eq "cidr") {
    $start = addr_to_decimal -addr $parsed[0]
    $start++ <# cidr notation starts at 0, an invalid host #>
    $range = 1 -shl (32 - $parsed[1]) <# find delta with left shift #>
    $range--
    $ping_to = decimal_to_addr -decimal $start
    $up_hosts = ping_range -addr $ping_to -range $range -quiet 0
  }
  else {
    return
  }
  write-host "Found " $up_hosts.count " hosts: "
  $up_hosts
}


function main_file_sweep {
  
  $user_file = read-host "Enter Filename >> "
  if(test-path -path $user_file) {
    [system.io.file]::readAllLines((Resolve-Path $user_file)) |
    % {
      $res += ping_range -addr $_ -range 1 -quiet 1
    }
    $res
  } else {
    main_file_sweep
  }
}


function main {
  $user_resp = read-host "1. Ping sweep from file`n2. Ping sweep range/cidr`n>> "
  if($user_resp -eq "1") {
    main_file_sweep
  } elseif ($user_resp -eq "2") {
    main_ping_sweep
  } else {
    main
  }
}


main

