##
# This module requires Metasploit: https://metasploit.com/download
# Current source: https://github.com/rapid7/metasploit-framework
##

class MetasploitModule < Msf::Auxiliary

  # Exploit mixins should be called first
  include Msf::Exploit::Remote::HttpClient
  include Msf::Auxiliary::WmapScanServer
  # Scanner mixin should be near last
  include Msf::Auxiliary::Scanner
  include Msf::Auxiliary::Report

  def initialize
    super(
      'Name'        => 'HTTP Options Detection',
      'Description' => 'Display available HTTP options for each system',
      'Author'       => ['CG'],
      'License'     => MSF_LICENSE,
      'References' =>
      [
        [ 'CVE', '2005-3398'],
        [ 'CVE', '2005-3498'],
        [ 'OSVDB', '877'],
        [ 'BID', '11604'],
        [ 'BID', '9506'],
        [ 'BID', '9561']
      ]
    )
  end

  def run_host(target_host)

    begin
      res = send_request_raw({
        'version'      => '1.0',
        'uri'          => '/',
        'method'       => 'OPTIONS'
      }, 10)

      if (res and res.headers['Allow'])
        print_good("#{target_host} allows #{res.headers['Allow']} methods")

        report_note(
          :host	=> target_host,
          :proto => 'tcp',
          :sname => (ssl ? 'https' : 'http'),
          :port	=> rport,
          :type	=> 'HTTP_OPTIONS',
          :data	=> res.headers['Allow']
        )

        if(res.headers['Allow'].index('TRACE'))
          print_good "#{target_host}:#{rport} - TRACE method allowed."
          report_vuln(
            :host	=> target_host,
            :port	=> rport,
            :proto => 'tcp',
            :sname => (ssl ? 'https' : 'http'),
            :name	=> "HTTP Trace Method Allowed",
            :info	=> "Module #{self.fullname} detected TRACE access through the Allow header: #{res.headers['Allow']}",
            :refs   => self.references,
            :exploited_at => Time.now.utc
          )
        end
      end

    rescue ::Rex::ConnectionRefused, ::Rex::HostUnreachable, ::Rex::ConnectionTimeout
    rescue ::Timeout::Error, ::Errno::EPIPE
    end
  end
end
