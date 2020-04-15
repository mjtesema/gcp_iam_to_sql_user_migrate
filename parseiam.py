#!/USR/bin/python
from absl import app
from absl import flags

FLAGS = flags.FLAGS
flags.DEFINE_string("iam_output_file", None, "Path to output of get-iam-policy command")
flags.mark_flag_as_required("iam_output_file")

# Note: some python style guide tips have been skipped to keep this code brief
#   Questions/Concerns: Please raise these via GitHub

CSQL_ADMIN = "roles/cloudsql.admin"
CSQL_EDITOR = "roles/cloudsql.editor"
CSQL_VIEWER = "roles/cloudsql.viewer"
PROJ_OWNER = "roles/owner"

SPLIT_PATTERN = "- members:"
ROLE_STR = "  role: roles/"
SVC_ACCT = "serviceAccount:"
USR = "user:"


def parse_resp_to_members(unformatted):
    if not unformatted:
        print("ERROR")
        exit(-1)
    else:
        formatted_members = []
        actual_member_counter = -1
        for member in unformatted:
            if SPLIT_PATTERN in member:
                actual_member_counter += 1
                formatted_members.insert(actual_member_counter, "")
                continue
            else:
                if not member:
                    continue
                current_value = formatted_members[actual_member_counter]
                next_value = current_value + member
                formatted_members[actual_member_counter] = next_value
        return formatted_members


def parse_members_to_roles(members):
    roles = []
    if len(members) == 0:
        print("ERROR_NO_CLOUDSQL_OR_OWNER_ROLES_FOR_PROJECT")
        exit(-1)
    else:
        for member in members:
            if ROLE_STR in member:
                roles.append(member)
            else:
                continue
        return roles


def super_strip(unstripped_str):
    if not unstripped_str:
        print("ERROR_TRYING_TO_STRIP_EMPTY_STRING")
        exit(-1)
    else:
        return unstripped_str.strip('\t').strip(' ').strip(' - ').strip("\n  ")


def trim_role_from_member(unformatted_member, role_str):
    if not unformatted_member or not role_str:
        print("ERROR_ATTEMPTED_TO_TRIM_BUT_MISSING_ROLE_OR_MEMBER")
        exit(-1)
    else:
        return super_strip(unformatted_member.replace("role: " + role_str, ""))


def generate_map_entry(role):
    if not role:
        print("ERROR_SENT_EMPTY_ROLE_TO_EXTRACT_IAM_ROLE_FROM")
        exit(-1)
    else:
        if PROJ_OWNER in role:
            return (PROJ_OWNER, trim_role_from_member(role, PROJ_OWNER))
        if CSQL_ADMIN in role:
            return (CSQL_ADMIN, trim_role_from_member(role, CSQL_ADMIN))
        if CSQL_EDITOR in role:
            return (CSQL_EDITOR, trim_role_from_member(role, CSQL_EDITOR))
        if CSQL_VIEWER in role:
            return (CSQL_VIEWER, trim_role_from_member(role, CSQL_VIEWER))


def map_roles_to_users(roles):
    role_map = {}
    if len(roles) == 0:
        print("ERROR_NO_ROLES_FOUND_IN_IAM_OUTPUT_AFTER_PARSING_FOR_ROLES")
        exit(-1)
    else:
        for role in roles:
            role_type, role_members = generate_map_entry(role)
            role_map[role_type] = role_members
    return role_map


def clean_role_type(uncleaned_role):
    cleaned_role = ""
    if not uncleaned_role:
        print("ERROR_ATTEMPTING_TO_REMOVE_USER_SVC_ACCT_FROM_NON_EXISTENT")
    else:
        if SVC_ACCT in uncleaned_role:
            cleaned_role = uncleaned_role.replace(SVC_ACCT, "")
        if USR in uncleaned_role:
            cleaned_role = uncleaned_role.replace(USR, "")
    return cleaned_role


def clean_expanded_roles(uncleaned_roles):
    cleaned_roles = []
    if not uncleaned_roles:
        print("ERROR_NO_ROW_ELEMENTS_WITH_USERS_SVC_ACCTS_TO_CLEAN")
    else:
        for each_uncleaned_role in uncleaned_roles:
            cleaned_roles.append(clean_role_type(each_uncleaned_role))
    return cleaned_roles


def expand_roles(role_str):
    if not role_str:
        print("ERROR_ATTEMPTING_TO_EXPAND_EMPTY_ROLE_STRING_TO_LIST")
        return ""
    else:
        roles = []
        print(role_str)
        return roles.split("\n - ")


def expand_mapped_roles(mapped_roles):
    expanded_role_map = {}
    if not mapped_roles:
        print("ERROR_ATTEMPTING_TO_EXPAND_MAP_THATS_NONEXISTENT")
        exit(-1)
    else:
        for key_item in mapped_roles.keys():
            roles = mapped_roles[key_item]
            expanded_roles = roles.split("\n  - ")
            expanded_roles_cleaned = clean_expanded_roles(expanded_roles)
            expanded_role_map[key_item] = expanded_roles_cleaned
    return expanded_role_map


def main(argv):
    del argv
    if FLAGS.iam_output_file is not None:
        with open(FLAGS.iam_output_file, "r") as f:
            content = f.readlines()
            if not content:
                print("EMPTY_OR_NON_PRESENT_FILE")
            else:
                parsed_members = parse_resp_to_members(content)
                parsed_roles = parse_members_to_roles(parsed_members)
                mapped_roles = map_roles_to_users(parsed_roles)
                expanded = expand_mapped_roles(mapped_roles)
                for expanded_role_key in expanded.keys():
                    for each_expanded in expanded[expanded_role_key]:
                        #print(expanded_role_key, end=" ")
                        print(each_expanded, end=" ")
                        #print("")


if __name__ == "__main__":
    app.run(main)