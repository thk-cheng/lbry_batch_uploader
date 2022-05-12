import os
import subprocess
from subprocess import PIPE, STDOUT, CompletedProcess


RFC5646_LANGUAGE_TAGS = {
    "af": "Afrikaans",
    "af-ZA": "Afrikaans (South Africa)",
    "ar": "Arabic",
    "ar-AE": "Arabic (U.A.E.)",
    "ar-BH": "Arabic (Bahrain)",
    "ar-DZ": "Arabic (Algeria)",
    "ar-EG": "Arabic (Egypt)",
    "ar-IQ": "Arabic (Iraq)",
    "ar-JO": "Arabic (Jordan)",
    "ar-KW": "Arabic (Kuwait)",
    "ar-LB": "Arabic (Lebanon)",
    "ar-LY": "Arabic (Libya)",
    "ar-MA": "Arabic (Morocco)",
    "ar-OM": "Arabic (Oman)",
    "ar-QA": "Arabic (Qatar)",
    "ar-SA": "Arabic (Saudi Arabia)",
    "ar-SY": "Arabic (Syria)",
    "ar-TN": "Arabic (Tunisia)",
    "ar-YE": "Arabic (Yemen)",
    "az": "Azeri (Latin)",
    "az-AZ": "Azeri (Latin) (Azerbaijan)",
    "az-Cyrl-AZ": "Azeri (Cyrillic) (Azerbaijan)",
    "be": "Belarusian",
    "be-BY": "Belarusian (Belarus)",
    "bg": "Bulgarian",
    "bg-BG": "Bulgarian (Bulgaria)",
    "bs-BA": "Bosnian (Bosnia and Herzegovina)",
    "ca": "Catalan",
    "ca-ES": "Catalan (Spain)",
    "cs": "Czech",
    "cs-CZ": "Czech (Czech Republic)",
    "cy": "Welsh",
    "cy-GB": "Welsh (United Kingdom)",
    "da": "Danish",
    "da-DK": "Danish (Denmark)",
    "de": "German",
    "de-AT": "German (Austria)",
    "de-CH": "German (Switzerland)",
    "de-DE": "German (Germany)",
    "de-LI": "German (Liechtenstein)",
    "de-LU": "German (Luxembourg)",
    "dv": "Divehi",
    "dv-MV": "Divehi (Maldives)",
    "el": "Greek",
    "el-GR": "Greek (Greece)",
    "en": "English",
    "en-AU": "English (Australia)",
    "en-BZ": "English (Belize)",
    "en-CA": "English (Canada)",
    "en-CB": "English (Caribbean)",
    "en-GB": "English (United Kingdom)",
    "en-IE": "English (Ireland)",
    "en-JM": "English (Jamaica)",
    "en-NZ": "English (New Zealand)",
    "en-PH": "English (Republic of the Philippines)",
    "en-TT": "English (Trinidad and Tobago)",
    "en-US": "English (United States)",
    "en-ZA": "English (South Africa)",
    "en-ZW": "English (Zimbabwe)",
    "eo": "Esperanto",
    "es": "Spanish",
    "es-AR": "Spanish (Argentina)",
    "es-BO": "Spanish (Bolivia)",
    "es-CL": "Spanish (Chile)",
    "es-CO": "Spanish (Colombia)",
    "es-CR": "Spanish (Costa Rica)",
    "es-DO": "Spanish (Dominican Republic)",
    "es-EC": "Spanish (Ecuador)",
    "es-ES": "Spanish (Spain)",
    "es-GT": "Spanish (Guatemala)",
    "es-HN": "Spanish (Honduras)",
    "es-MX": "Spanish (Mexico)",
    "es-NI": "Spanish (Nicaragua)",
    "es-PA": "Spanish (Panama)",
    "es-PE": "Spanish (Peru)",
    "es-PR": "Spanish (Puerto Rico)",
    "es-PY": "Spanish (Paraguay)",
    "es-SV": "Spanish (El Salvador)",
    "es-UY": "Spanish (Uruguay)",
    "es-VE": "Spanish (Venezuela)",
    "et": "Estonian",
    "et-EE": "Estonian (Estonia)",
    "eu": "Basque",
    "eu-ES": "Basque (Spain)",
    "fa": "Farsi",
    "fa-IR": "Farsi (Iran)",
    "fi": "Finnish",
    "fi-FI": "Finnish (Finland)",
    "fo": "Faroese",
    "fo-FO": "Faroese (Faroe Islands)",
    "fr": "French",
    "fr-BE": "French (Belgium)",
    "fr-CA": "French (Canada)",
    "fr-CH": "French (Switzerland)",
    "fr-FR": "French (France)",
    "fr-LU": "French (Luxembourg)",
    "fr-MC": "French (Principality of Monaco)",
    "gl": "Galician",
    "gl-ES": "Galician (Spain)",
    "gu": "Gujarati",
    "gu-IN": "Gujarati (India)",
    "he": "Hebrew",
    "he-IL": "Hebrew (Israel)",
    "hi": "Hindi",
    "hi-IN": "Hindi (India)",
    "hr": "Croatian",
    "hr-BA": "Croatian (Bosnia and Herzegovina)",
    "hr-HR": "Croatian (Croatia)",
    "hu": "Hungarian",
    "hu-HU": "Hungarian (Hungary)",
    "hy": "Armenian",
    "hy-AM": "Armenian (Armenia)",
    "id": "Indonesian",
    "id-ID": "Indonesian (Indonesia)",
    "is": "Icelandic",
    "is-IS": "Icelandic (Iceland)",
    "it": "Italian",
    "it-CH": "Italian (Switzerland)",
    "it-IT": "Italian (Italy)",
    "ja": "Japanese",
    "ja-JP": "Japanese (Japan)",
    "ka": "Georgian",
    "ka-GE": "Georgian (Georgia)",
    "kk": "Kazakh",
    "kk-KZ": "Kazakh (Kazakhstan)",
    "kn": "Kannada",
    "kn-IN": "Kannada (India)",
    "ko": "Korean",
    "ko-KR": "Korean (Korea)",
    "kok": "Konkani",
    "kok-IN": "Konkani (India)",
    "ky": "Kyrgyz",
    "ky-KG": "Kyrgyz (Kyrgyzstan)",
    "lt": "Lithuanian",
    "lt-LT": "Lithuanian (Lithuania)",
    "lv": "Latvian",
    "lv-LV": "Latvian (Latvia)",
    "mi": "Maori",
    "mi-NZ": "Maori (New Zealand)",
    "mk": "FYRO Macedonian",
    "mk-MK": "FYRO Macedonian (Former Yugoslav Republic of Macedonia)",
    "mn": "Mongolian",
    "mn-MN": "Mongolian (Mongolia)",
    "mr": "Marathi",
    "mr-IN": "Marathi (India)",
    "ms": "Malay",
    "ms-BN": "Malay (Brunei Darussalam)",
    "ms-MY": "Malay (Malaysia)",
    "mt": "Maltese",
    "mt-MT": "Maltese (Malta)",
    "nb": "Norwegian (Bokm?l)",
    "nb-NO": "Norwegian (Bokm?l) (Norway)",
    "nl": "Dutch",
    "nl-BE": "Dutch (Belgium)",
    "nl-NL": "Dutch (Netherlands)",
    "nn-NO": "Norwegian (Nynorsk) (Norway)",
    "ns": "Northern Sotho",
    "ns-ZA": "Northern Sotho (South Africa)",
    "pa": "Punjabi",
    "pa-IN": "Punjabi (India)",
    "pl": "Polish",
    "pl-PL": "Polish (Poland)",
    "ps": "Pashto",
    "ps-AR": "Pashto (Afghanistan)",
    "pt": "Portuguese",
    "pt-BR": "Portuguese (Brazil)",
    "pt-PT": "Portuguese (Portugal)",
    "qu": "Quechua",
    "qu-BO": "Quechua (Bolivia)",
    "qu-EC": "Quechua (Ecuador)",
    "qu-PE": "Quechua (Peru)",
    "ro": "Romanian",
    "ro-RO": "Romanian (Romania)",
    "ru": "Russian",
    "ru-RU": "Russian (Russia)",
    "sa": "Sanskrit",
    "sa-IN": "Sanskrit (India)",
    "se": "Sami",
    "se-FI": "Sami (Finland)",
    "se-NO": "Sami (Norway)",
    "se-SE": "Sami (Sweden)",
    "sk": "Slovak",
    "sk-SK": "Slovak (Slovakia)",
    "sl": "Slovenian",
    "sl-SI": "Slovenian (Slovenia)",
    "sq": "Albanian",
    "sq-AL": "Albanian (Albania)",
    "sr-BA": "Serbian (Latin) (Bosnia and Herzegovina)",
    "sr-Cyrl-BA": "Serbian (Cyrillic) (Bosnia and Herzegovina)",
    "sr-SP": "Serbian (Latin) (Serbia and Montenegro)",
    "sr-Cyrl-SP": "Serbian (Cyrillic) (Serbia and Montenegro)",
    "sv": "Swedish",
    "sv-FI": "Swedish (Finland)",
    "sv-SE": "Swedish (Sweden)",
    "sw": "Swahili",
    "sw-KE": "Swahili (Kenya)",
    "syr": "Syriac",
    "syr-SY": "Syriac (Syria)",
    "ta": "Tamil",
    "ta-IN": "Tamil (India)",
    "te": "Telugu",
    "te-IN": "Telugu (India)",
    "th": "Thai",
    "th-TH": "Thai (Thailand)",
    "tl": "Tagalog",
    "tl-PH": "Tagalog (Philippines)",
    "tn": "Tswana",
    "tn-ZA": "Tswana (South Africa)",
    "tr": "Turkish",
    "tr-TR": "Turkish (Turkey)",
    "tt": "Tatar",
    "tt-RU": "Tatar (Russia)",
    "ts": "Tsonga",
    "uk": "Ukrainian",
    "uk-UA": "Ukrainian (Ukraine)",
    "ur": "Urdu",
    "ur-PK": "Urdu (Islamic Republic of Pakistan)",
    "uz": "Uzbek (Latin)",
    "uz-UZ": "Uzbek (Latin) (Uzbekistan)",
    "uz-Cyrl-UZ": "Uzbek (Cyrillic) (Uzbekistan)",
    "vi": "Vietnamese",
    "vi-VN": "Vietnamese (Viet Nam)",
    "xh": "Xhosa",
    "xh-ZA": "Xhosa (South Africa)",
    "zh": "Chinese",
    "zh-CN": "Chinese (Simplified)",
    "zh-Hant": "Chinese (Traditional)",
    "zh-HK": "Chinese (Hong Kong)",
    "zh-MO": "Chinese (Macau)",
    "zh-SG": "Chinese (Singapore)",
    "zh-TW": "Chinese (Taiwan)",
    "zu": "Zulu",
    "zu-ZA": "Zulu (South Africa)",
}

LICENSES = [
    "Public Domain",
    "Creative Commons Attribution 4.0 International",
    "Creative Commons Attribution-ShareAlike 4.0 International",
    "Creative Commons Attribution-NoDerivatives 4.0 International",
    "Creative Commons Attribution-NonCommercial 4.0 International",
    "Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International",
    "Creative Commons Attribution-NonCommercial-NoDerivatives 4.0 International",
    "Copyrighted (All rights reserved)",
    "Other",
    ]


class Error(Exception):
    """Base class for other exceptions."""
    pass

class ConnectionError(Exception):
    """Exception raised for error in connecting with lbrynet."""
    pass

class PipeError(Error):
    """Exception raised for error in piping commands."""
    pass


# class ThumbnailCreationError(Error):
#     """
#     Exception raised for error in creating thumbnail from an input.
# 
#     Attributes
#     ----------
#     file_name_absolute: str
#         The absolute path of the input file
# 
#     p: subprocess.CompletedProcess
#         An instance of CompletedProcess for the command
#             that attempts to create the thumbnail
# 
#     """
# 
#     def __init__(self, file_name_absolute: str, p: CompletedProcess):
#         self.file_name_absolute = file_name_absolute
#         self.p = p
#         super().__init__()
# 
#     def __str__(self):
#         return f"Fail to create thumbnail for {self.file_name_absolute}"
 

def get_file_name_no_ext(file_name_with_ext: str) -> str:
    """
    Get the name of the input file without extension.

    Parameters
    ----------
    file_name_with_ext: str
        The name of input file with extension

    Returns
    -------
    str
        The name of the input file without extension

    """

    try:
        name_parts = file_name_with_ext.split(".")[0:-1]
    except AttributeError:
        raise TypeError("file_name_with_ext must be a string") from None

    # Join the parts back together with ".", as the original name may contain "."
    return ".".join(name_parts)


def get_file_name_no_ext_clean(file_name_no_ext: str) -> str:
    """
    Clean the file name without extension so that no special characters exist

    Parameters
    ----------
    file_name_no_ext: str
        The name of input file without extension

    Returns
    -------
    str
        Cleaned version of the file name without extension
    """

    bad_chars_half = "!@#$%^&*()_+=}{|:;'<,>?/" + '"' + "\\"
    bad_chars_full = """！％……＊（）——『〖｛「【〔［ \
                        〚〘』〗｝」】〕］〛〙·・｜、\
                        ＼：；“‘《〈，》〉。？"""
    bad_chars = bad_chars_half + bad_chars_full
    mapping = str.maketrans({bad_char: None for bad_char in bad_chars})

    return file_name_no_ext.translate(mapping)


# def create_thumbnail(base_path: str, file_name: str) -> str:
#     """
#     Create a thumbnail from the input file.
# 
#     The selected frame is chosen to be at the middle of the input file.
# 
#     Parameters
#     ----------
#     base_path: str
#         The base path which contains the input file
# 
#     file_name: str
#         The name of input file with extension
# 
#     Returns
#     -------
#     str
#         The name of the thumbnail with extension
# 
#     """
# 
#     file_name_absolute = os.path.join(base_path, file_name)
#     thumbnail_name = f"{get_file_name_no_ext(file_name)}.png"
#     thumbnail_name_absolute = os.path.join(base_path, thumbnail_name)
# 
#     # Explanation for all the commands below:
#     #   cmd_0: Get info of the input file by ffmpeg
#     #   cmd_1: Grep the line that contains the duration of input file
#     #   cmd_2: Isolate the duration of video from that line
#     #   cmd_3: Remove trailing comma
#     #   cmd_4: Find the time corresponds to the middle of the input file
#     #   cmd_5: Actual command that creates the thumbnail by ffmpeg
# 
#     cmd_0 = ["ffmpeg", "-i", file_name_absolute]
#     cmd_1 = ["grep", "Duration"]
#     cmd_2 = ["awk", "{print $2}"]
#     cmd_3 = ["tr", "-d", ","]
#     cmd_4 = ["awk", "-F", ":", "{print ($3+$2*60+$1*3600)/2}"]
# 
#     # Same as adding "2>&1" at the end of cmd_0
#     p = subprocess.run(cmd_0, stdout=PIPE, stderr=STDOUT, text=True)
# 
#     # Pipe commands from cmd_0 to cmd_4
#     p = _pipe_cmds([cmd_1, cmd_2, cmd_3, cmd_4], prev_p=p)
# 
#     # # Format the delayed start time as "00:00:00.000"
#     # delayed_time_in_sec = float(p.stdout)
#     # delayed_hour = delayed_time_in_sec // 3600
#     # delayed_min = (delayed_time_in_sec - delayed_hour * 3600) // 60
#     # delayed_sec, delayed_millisec = divmod(delayed_time_in_sec - delayed_hour * 3600 - delayed_min * 60, 1)
#     # delayed_start_time = f"{int(delayed_hour):02}:{int(delayed_min):02}:{int(delayed_sec):02}.{delayed_millisec*1000:.0f}"
# 
#     # Get the delayed start time from p
#     delayed_start_time = str(float(p.stdout))
# 
#     cmd_5 = [
#         "ffmpeg",
#         "-y",
#         "-i", file_name_absolute,
#         "-frames:v", "1",
#         "-ss", delayed_start_time,
#         thumbnail_name_absolute
#     ]
# 
#     p1 = subprocess.run(cmd_5, capture_output=True, text=True)
# 
#     if p1.returncode != 0:
#         raise ThumbnailCreationError(file_name_absolute, p1)
#     else:
#         print(f"Successfully created thumbnail for {file_name_absolute}")
# 
#     return thumbnail_name
 

def _pipe_cmds(cmds: list[list[str]], *, prev_p: CompletedProcess = None) -> CompletedProcess:
    """
    Piping commands using the subprocess module.

    Parameters
    ----------
    cmds: list[str]
        A list that stores all the commands

    prev_p: subprocess.CompletedProcess (Optional)
        An instance of CompletedProcess for the previous command

    Returns
    -------
    p: subprocess.CompletedProcess
        An instance of CompletedProcess for the final result

    """

    if not isinstance(cmds, list):
        raise TypeError("cmds must be a list")

    if not isinstance(cmds[0], list) or len(cmds)<2:
        raise PipeError("At least two commands are needed for piping")

    if prev_p is not None:
        p = prev_p
    else:
        p = subprocess.run(cmd[0], capture_output=True, text=True)
        cmds = cmds[1:]

    for cmd in cmds:
        p = subprocess.run(cmd, capture_output=True, text=True, input=p.stdout)

    return p


if __name__ == "__main__":
    pass
