import os
from grafana_backup.dashboardApi import get_all_library_elements
from grafana_backup.commons import to_python2_and_3_compatible_string, print_horizontal_line, save_json


def main(args, settings):
    backup_dir = settings.get('BACKUP_DIR')
    timestamp = settings.get('TIMESTAMP')
    grafana_url = settings.get('GRAFANA_URL')
    http_get_headers = settings.get('HTTP_GET_HEADERS')
    verify_ssl = settings.get('VERIFY_SSL')
    client_cert = settings.get('CLIENT_CERT')
    debug = settings.get('DEBUG')
    pretty_print = settings.get('PRETTY_PRINT')

    folder_path = '{0}/library_elements/{1}'.format(backup_dir, timestamp)
    log_file = 'library_elements_{0}.txt'.format(timestamp)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    library_elements = get_all_library_elements_from_grafana(grafana_url, http_get_headers, verify_ssl, client_cert, debug)
    get_individual_library_element_and_save(library_elements, folder_path, log_file, pretty_print)
    print_horizontal_line()


def get_all_library_elements_from_grafana(grafana_url, http_get_headers, verify_ssl, client_cert, debug):
    (status, content) = get_all_library_elements(grafana_url, http_get_headers, verify_ssl, client_cert, debug)
    if status == 200:
        elements = content.get('result', {}).get('elements', [])
        print("There are {0} library elements:".format(len(elements)))
        for element in elements:
            print("name: {0}, uid: {1}".format(to_python2_and_3_compatible_string(element['name']), element['uid']))
        return elements
    else:
        print("Query library elements failed, status: {0}, msg: {1}".format(status, content))
        return []


def save_library_element(element_name, file_name, library_element, folder_path, pretty_print):
    file_path = save_json(file_name, library_element, folder_path, 'library_element', pretty_print)
    print("library_element:{0} is saved to {1}".format(element_name, file_path))


def get_individual_library_element_and_save(elements, folder_path, log_file, pretty_print):
    file_path = folder_path + '/' + log_file
    if elements:
        with open(u"{0}".format(file_path), 'w') as f:
            for element in elements:
                if 'uid' in element:
                    element_identifier = element['uid']
                else:
                    element_identifier = element['id']

                save_library_element(
                    to_python2_and_3_compatible_string(element['name']),
                    to_python2_and_3_compatible_string(str(element_identifier)),
                    element,
                    folder_path,
                    pretty_print
                )
                f.write('{0}\t{1}\n'.format(to_python2_and_3_compatible_string(str(element_identifier)),
                                            to_python2_and_3_compatible_string(element['name'])))
