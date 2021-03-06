/*
This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
*/

/*
ADD DATA: -----------------------------------------------------------

Here we add data from local sources to `flowdb`.
The data added at the moment is:

  - operator_database.csv:
  - tac_database.:

---------------------------------------------------------------------
*/
COPY infrastructure.operators(id, name, country, iso)
    FROM '/docker-entrypoint-initdb.d/data/csv/operator_database.csv'
        WITH DELIMITER ','
        CSV HEADER;

COPY infrastructure.tacs(id, brand, model, width, height, depth,
    weight, display_type, display_colors, display_width,
    display_height, mms_receiver, mms_built_in_camera,
    wap_push_ota_support, hardware_gprs, hardware_edge,
    hardware_umts, hardware_wifi, hardware_bluetooth, hardware_gps,
    software_os_vendor, software_os_name, software_os_version,
    wap_push_ota_settings, wap_push_ota_bookmarks,
    wap_push_ota_app_internet, wap_push_ota_app_browser,
    wap_push_ota_app_mms, wap_push_ota_single_shot,
    wap_push_ota_multi_shot, wap_push_oma_settings,
    wap_push_oma_app_internet, wap_push_oma_app_browser,
    wap_push_oma_app_mms, wap_push_oma_cp_bookmarks,
    wap_1_2_1, wap_2_0, syncml_dm_settings, syncml_dm_acc_gprs,
    syncml_dm_app_internet, syncml_dm_app_browser, syncml_dm_app_mms,
    syncml_dm_app_bookmark, syncml_dm_app_java, wap_push_oma_app_ims,
    wap_push_oma_app_poc, j2me_midp_10, j2me_midp_20, j2me_midp_21,
    j2me_cldc_10, j2me_cldc_11, j2me_cldc_20, hnd_type)
    FROM '/docker-entrypoint-initdb.d/data/csv/tac_database.csv'
        WITH DELIMITER ','
        CSV HEADER;
