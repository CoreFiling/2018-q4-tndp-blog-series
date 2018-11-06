<?php
defined( 'ABSPATH' ) or die( 'Not to be referenced directly' );

/*
Plugin Name:  CoreFiling TNDP Table Renderer
Plugin URI:   https://www.corefiling.com
Version:      201811061054
Description:  Allows rendering of tables from the TNDP
Author:       CoreFiling
Author URI:   https://www.corefiling.com
License:      Apache 2.0
*/

define('SERVICE_CLIENT_NAME', '(insert yours)');
define('SERVICE_CLIENT_SECRET', '(insert yours)');
define('BASE_URL', 'https://api.labs.corefiling.com/');

define('TABLE_ID', 'f4f40535-8d99-4608-9c8a-a98d6cc4990e'); // Replace with a table ID from one of your own labs filings


// Thanks to https://www.weichieprojects.com/blog/curl-api-calls-with-php/
function callAPI($method, $url, $data, $token){
   $curl = curl_init();

   switch ($method){
      case "POST":
         curl_setopt($curl, CURLOPT_POST, 1);
         curl_setopt($curl, CURLOPT_POSTFIELDS, http_build_query($data));
         break;
   }

   if ($token != "") {
	   $auth_header = "Authorization: Bearer ".$token;
	   curl_setopt($curl, CURLOPT_HTTPHEADER, array(
         $auth_header
       ));
   }
   else {
	   // HTTP basic auth with service account credentials
	   curl_setopt($curl, CURLOPT_HTTPAUTH, CURLAUTH_BASIC);
	   curl_setopt($curl, CURLOPT_USERPWD, SERVICE_CLIENT_NAME . ":" . SERVICE_CLIENT_SECRET);
   }

   curl_setopt($curl, CURLOPT_URL, $url);
   curl_setopt($curl, CURLOPT_RETURNTRANSFER, 1);

   $result = curl_exec($curl);
   if(!$result){die("Connection Failure");}

   curl_close($curl);
   return $result;
}


function get_table_html() {
  $result = "";

  # Authenticate and obtain access token.
  $at_response = callAPI("POST", "https://login.corefiling.com/auth/realms/platform/protocol/openid-connect/token", array("grant_type" => "client_credentials"), "");
  $access_token = json_decode($at_response, true)['access_token'];

  $table_req = callAPI("GET", BASE_URL.'table-rendering-service/v1/tables/'.TABLE_ID.'/render/?x=0&y=0&z=0&width=1000&height=10000', array(), $access_token);

  # Naive rendering assuming a simple table with two columns. A proper table widget would be used in the general case.
  $result .= "<table>";

  $rj = json_decode($table_req, true);

  $header_rows = $rj['yAxis'];
  $data_rows = $rj['data'];
  $row_count = count($header_rows);

  for ($x=0; $x<$row_count; $x++) {
    $labels = array();
    $first = true;
    foreach ($header_rows[$x] as $c) {
      if ($first) {
        $first=false;
      }
      else {
        array_push($labels, $c['name']);
      }
    }

    $data = $data_rows[0][$x];
    if($data != null){
      $data = $data['facts'][0]['stringValue'];
    }
    else {
      $data = "";
    }
    $result .= sprintf("<tr><td>%s</td><td>%s</td><td>%s</td></tr>", $labels[0], $labels[1], $data);
  }

  $result .=  "</table>";
  return $result;
}


function cfl_content_filter($content) {
  $cfl_tag = "[cfl_tndp_table]";
  if(strpos($content, $cfl_tag) !== FALSE) {
    return str_replace($cfl_tag, get_table_html(), $content);
  }
  return $content;
}

add_filter('the_content', 'cfl_content_filter'); // Table display (replaces our magic tag in any page/post bodies)

?>
