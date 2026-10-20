"""生成 Wobi.xcodeproj/project.pbxproj 和共享 scheme。

这个仓库里没有 Mac，所以工程文件是脚本生成的；在 Mac 上正常用 Xcode 打开即可。
新增 Swift 文件时，改 FILES 列表后重新运行：

    python tools/make_project.py
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT / "Wobi.xcodeproj"

FILES = [
    "WobiApp.swift",
    "Models.swift",
    "SettingsStore.swift",
    "ChatClient.swift",
    "ChatStore.swift",
    "ImageTool.swift",
    "ChatView.swift",
    "SettingsView.swift",
]


def oid(prefix: str, number: int) -> str:
    return f"{prefix}{number:022d}"


# 固定 ID，保证重复运行结果一致
FILE_REF = {name: oid("A1", index + 1) for index, name in enumerate(FILES)}
ASSETS_REF = oid("A1", 101)
PRIVACY_REF = oid("A1", 102)
INFO_REF = oid("A1", 103)
PRODUCT_REF = oid("A1", 104)

BUILD = {name: oid("B1", index + 1) for index, name in enumerate(FILES)}
ASSETS_BUILD = oid("B1", 101)
PRIVACY_BUILD = oid("B1", 102)

MAIN_GROUP = oid("C1", 1)
WOBI_GROUP = oid("C1", 2)
SOURCES_GROUP = oid("C1", 3)
PRODUCTS_GROUP = oid("C1", 4)

SOURCES_PHASE = oid("D1", 1)
FRAMEWORKS_PHASE = oid("D1", 2)
RESOURCES_PHASE = oid("D1", 3)

TARGET = oid("E1", 1)
PROJECT_ID = oid("E1", 2)

PROJECT_DEBUG = oid("F1", 1)
PROJECT_RELEASE = oid("F1", 2)
TARGET_DEBUG = oid("F1", 3)
TARGET_RELEASE = oid("F1", 4)
PROJECT_CONFIG_LIST = oid("F2", 1)
TARGET_CONFIG_LIST = oid("F2", 2)

COMMON_WARNINGS = """
\t\t\t\tALWAYS_SEARCH_USER_PATHS = NO;
\t\t\t\tASSETCATALOG_COMPILER_GENERATE_SWIFT_ASSET_SYMBOL_EXTENSIONS = YES;
\t\t\t\tCLANG_ANALYZER_NONNULL = YES;
\t\t\t\tCLANG_ANALYZER_NUMBER_OBJECT_CONVERSION = YES_AGGRESSIVE;
\t\t\t\tCLANG_CXX_LANGUAGE_STANDARD = "gnu++20";
\t\t\t\tCLANG_ENABLE_MODULES = YES;
\t\t\t\tCLANG_ENABLE_OBJC_ARC = YES;
\t\t\t\tCLANG_ENABLE_OBJC_WEAK = YES;
\t\t\t\tCLANG_WARN_BLOCK_CAPTURE_AUTORELEASING = YES;
\t\t\t\tCLANG_WARN_BOOL_CONVERSION = YES;
\t\t\t\tCLANG_WARN_COMMA = YES;
\t\t\t\tCLANG_WARN_CONSTANT_CONVERSION = YES;
\t\t\t\tCLANG_WARN_DEPRECATED_OBJC_IMPLEMENTATIONS = YES;
\t\t\t\tCLANG_WARN_DIRECT_OBJC_ISA_USAGE = YES_ERROR;
\t\t\t\tCLANG_WARN_DOCUMENTATION_COMMENTS = YES;
\t\t\t\tCLANG_WARN_EMPTY_BODY = YES;
\t\t\t\tCLANG_WARN_ENUM_CONVERSION = YES;
\t\t\t\tCLANG_WARN_INFINITE_RECURSION = YES;
\t\t\t\tCLANG_WARN_INT_CONVERSION = YES;
\t\t\t\tCLANG_WARN_NON_LITERAL_NULL_CONVERSION = YES;
\t\t\t\tCLANG_WARN_OBJC_IMPLICIT_RETAIN_SELF = YES;
\t\t\t\tCLANG_WARN_OBJC_LITERAL_CONVERSION = YES;
\t\t\t\tCLANG_WARN_OBJC_ROOT_CLASS = YES_ERROR;
\t\t\t\tCLANG_WARN_QUOTED_INCLUDE_IN_FRAMEWORK_HEADER = YES;
\t\t\t\tCLANG_WARN_RANGE_LOOP_ANALYSIS = YES;
\t\t\t\tCLANG_WARN_STRICT_PROTOTYPES = YES;
\t\t\t\tCLANG_WARN_SUSPICIOUS_MOVE = YES;
\t\t\t\tCLANG_WARN_UNGUARDED_AVAILABILITY = YES_AGGRESSIVE;
\t\t\t\tCLANG_WARN_UNREACHABLE_CODE = YES;
\t\t\t\tCLANG_WARN__DUPLICATE_METHOD_MATCH = YES;
\t\t\t\tCOPY_PHASE_STRIP = NO;
\t\t\t\tENABLE_STRICT_OBJC_MSGSEND = YES;
\t\t\t\tENABLE_USER_SCRIPT_SANDBOXING = YES;
\t\t\t\tGCC_C_LANGUAGE_STANDARD = gnu17;
\t\t\t\tGCC_NO_COMMON_BLOCKS = YES;
\t\t\t\tGCC_WARN_64_TO_32_BIT_CONVERSION = YES;
\t\t\t\tGCC_WARN_ABOUT_RETURN_TYPE = YES_ERROR;
\t\t\t\tGCC_WARN_UNDECLARED_SELECTOR = YES;
\t\t\t\tGCC_WARN_UNINITIALIZED_AUTOS = YES_AGGRESSIVE;
\t\t\t\tGCC_WARN_UNUSED_FUNCTION = YES;
\t\t\t\tGCC_WARN_UNUSED_VARIABLE = YES;
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 17.0;
\t\t\t\tLOCALIZATION_PREFERS_STRING_CATALOGS = YES;
\t\t\t\tMTL_FAST_MATH = YES;
\t\t\t\tSDKROOT = iphoneos;
""".strip("\n")

DEBUG_ONLY = """
\t\t\t\tDEBUG_INFORMATION_FORMAT = dwarf;
\t\t\t\tENABLE_TESTABILITY = YES;
\t\t\t\tGCC_DYNAMIC_NO_PIC = NO;
\t\t\t\tGCC_OPTIMIZATION_LEVEL = 0;
\t\t\t\tGCC_PREPROCESSOR_DEFINITIONS = (
\t\t\t\t\t"DEBUG=1",
\t\t\t\t\t"$(inherited)",
\t\t\t\t);
\t\t\t\tMTL_ENABLE_DEBUG_INFO = INCLUDE_SOURCE;
\t\t\t\tONLY_ACTIVE_ARCH = YES;
\t\t\t\tSWIFT_ACTIVE_COMPILATION_CONDITIONS = "DEBUG $(inherited)";
\t\t\t\tSWIFT_OPTIMIZATION_LEVEL = "-Onone";
""".strip("\n")

RELEASE_ONLY = """
\t\t\t\tDEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
\t\t\t\tENABLE_NS_ASSERTIONS = NO;
\t\t\t\tMTL_ENABLE_DEBUG_INFO = NO;
\t\t\t\tSWIFT_COMPILATION_MODE = wholemodule;
\t\t\t\tSWIFT_OPTIMIZATION_LEVEL = "-O";
\t\t\t\tVALIDATE_PRODUCT = YES;
""".strip("\n")

TARGET_SETTINGS = """
\t\t\t\tASSETCATALOG_COMPILER_APPICON_NAME = AppIcon;
\t\t\t\tASSETCATALOG_COMPILER_GLOBAL_ACCENT_COLOR_NAME = AccentColor;
\t\t\t\tCODE_SIGN_STYLE = Automatic;
\t\t\t\tCURRENT_PROJECT_VERSION = 1;
\t\t\t\tENABLE_PREVIEWS = YES;
\t\t\t\tGENERATE_INFOPLIST_FILE = NO;
\t\t\t\tINFOPLIST_FILE = Wobi/Info.plist;
\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 17.0;
\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t"$(inherited)",
\t\t\t\t\t"@executable_path/Frameworks",
\t\t\t\t);
\t\t\t\tMARKETING_VERSION = 1.0;
\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = com.wobi.app;
\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\tSUPPORTED_PLATFORMS = "iphoneos iphonesimulator";
\t\t\t\tSUPPORTS_MACCATALYST = NO;
\t\t\t\tSUPPORTS_MAC_DESIGNED_FOR_IPHONE_IPAD = NO;
\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t\tTARGETED_DEVICE_FAMILY = 1;
""".strip("\n")


def build_file_section() -> str:
    lines = ["/* Begin PBXBuildFile section */"]
    for name in FILES:
        lines.append(
            f"\t\t{BUILD[name]} /* {name} in Sources */ = "
            f"{{isa = PBXBuildFile; fileRef = {FILE_REF[name]} /* {name} */; }};"
        )
    lines.append(
        f"\t\t{ASSETS_BUILD} /* Assets.xcassets in Resources */ = "
        f"{{isa = PBXBuildFile; fileRef = {ASSETS_REF} /* Assets.xcassets */; }};"
    )
    lines.append(
        f"\t\t{PRIVACY_BUILD} /* PrivacyInfo.xcprivacy in Resources */ = "
        f"{{isa = PBXBuildFile; fileRef = {PRIVACY_REF} /* PrivacyInfo.xcprivacy */; }};"
    )
    lines.append("/* End PBXBuildFile section */")
    return "\n".join(lines)


def file_reference_section() -> str:
    lines = ["/* Begin PBXFileReference section */"]
    for name in FILES:
        lines.append(
            f"\t\t{FILE_REF[name]} /* {name} */ = "
            f"{{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; "
            f'path = "{name}"; sourceTree = "<group>"; }};'
        )
    lines.append(
        f"\t\t{ASSETS_REF} /* Assets.xcassets */ = "
        f"{{isa = PBXFileReference; lastKnownFileType = folder.assetcatalog; "
        f'path = "Assets.xcassets"; sourceTree = "<group>"; }};'
    )
    lines.append(
        f"\t\t{PRIVACY_REF} /* PrivacyInfo.xcprivacy */ = "
        f"{{isa = PBXFileReference; lastKnownFileType = text.xml; "
        f'path = "PrivacyInfo.xcprivacy"; sourceTree = "<group>"; }};'
    )
    lines.append(
        f"\t\t{INFO_REF} /* Info.plist */ = "
        f"{{isa = PBXFileReference; lastKnownFileType = text.plist.xml; "
        f'path = "Info.plist"; sourceTree = "<group>"; }};'
    )
    lines.append(
        f"\t\t{PRODUCT_REF} /* Wobi.app */ = "
        f"{{isa = PBXFileReference; explicitFileType = wrapper.application; "
        f'includeInIndex = 0; path = "Wobi.app"; sourceTree = BUILT_PRODUCTS_DIR; }};'
    )
    lines.append("/* End PBXFileReference section */")
    return "\n".join(lines)


def group_section() -> str:
    source_children = "\n".join(
        f"\t\t\t\t{FILE_REF[name]} /* {name} */," for name in FILES
    )
    return f"""/* Begin PBXGroup section */
\t\t{MAIN_GROUP} = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{WOBI_GROUP} /* Wobi */,
\t\t\t\t{PRODUCTS_GROUP} /* Products */,
\t\t\t);
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{WOBI_GROUP} /* Wobi */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{SOURCES_GROUP} /* Sources */,
\t\t\t\t{ASSETS_REF} /* Assets.xcassets */,
\t\t\t\t{PRIVACY_REF} /* PrivacyInfo.xcprivacy */,
\t\t\t\t{INFO_REF} /* Info.plist */,
\t\t\t);
\t\t\tpath = Wobi;
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{SOURCES_GROUP} /* Sources */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
{source_children}
\t\t\t);
\t\t\tpath = Sources;
\t\t\tsourceTree = "<group>";
\t\t}};
\t\t{PRODUCTS_GROUP} /* Products */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{PRODUCT_REF} /* Wobi.app */,
\t\t\t);
\t\t\tname = Products;
\t\t\tsourceTree = "<group>";
\t\t}};
/* End PBXGroup section */"""


def phases_section() -> str:
    source_files = "\n".join(
        f"\t\t\t\t{BUILD[name]} /* {name} in Sources */," for name in FILES
    )
    return f"""/* Begin PBXFrameworksBuildPhase section */
\t\t{FRAMEWORKS_PHASE} /* Frameworks */ = {{
\t\t\tisa = PBXFrameworksBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXFrameworksBuildPhase section */

/* Begin PBXResourcesBuildPhase section */
\t\t{RESOURCES_PHASE} /* Resources */ = {{
\t\t\tisa = PBXResourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t\t{ASSETS_BUILD} /* Assets.xcassets in Resources */,
\t\t\t\t{PRIVACY_BUILD} /* PrivacyInfo.xcprivacy in Resources */,
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXResourcesBuildPhase section */

/* Begin PBXSourcesBuildPhase section */
\t\t{SOURCES_PHASE} /* Sources */ = {{
\t\t\tisa = PBXSourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
{source_files}
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXSourcesBuildPhase section */"""


def target_section() -> str:
    return f"""/* Begin PBXNativeTarget section */
\t\t{TARGET} /* Wobi */ = {{
\t\t\tisa = PBXNativeTarget;
\t\t\tbuildConfigurationList = {TARGET_CONFIG_LIST} /* Build configuration list for PBXNativeTarget "Wobi" */;
\t\t\tbuildPhases = (
\t\t\t\t{SOURCES_PHASE} /* Sources */,
\t\t\t\t{FRAMEWORKS_PHASE} /* Frameworks */,
\t\t\t\t{RESOURCES_PHASE} /* Resources */,
\t\t\t);
\t\t\tbuildRules = (
\t\t\t);
\t\t\tdependencies = (
\t\t\t);
\t\t\tname = Wobi;
\t\t\tproductName = Wobi;
\t\t\tproductReference = {PRODUCT_REF} /* Wobi.app */;
\t\t\tproductType = "com.apple.product-type.application";
\t\t}};
/* End PBXNativeTarget section */"""


def project_section() -> str:
    return f"""/* Begin PBXProject section */
\t\t{PROJECT_ID} /* Project object */ = {{
\t\t\tisa = PBXProject;
\t\t\tattributes = {{
\t\t\t\tBuildIndependentTargetsInParallel = 1;
\t\t\t\tLastSwiftUpdateCheck = 1500;
\t\t\t\tLastUpgradeCheck = 1500;
\t\t\t\tTargetAttributes = {{
\t\t\t\t\t{TARGET} = {{
\t\t\t\t\t\tCreatedOnToolsVersion = 15.0;
\t\t\t\t\t}};
\t\t\t\t}};
\t\t\t}};
\t\t\tbuildConfigurationList = {PROJECT_CONFIG_LIST} /* Build configuration list for PBXProject "Wobi" */;
\t\t\tcompatibilityVersion = "Xcode 14.0";
\t\t\tdevelopmentRegion = "zh-Hans";
\t\t\thasScannedForEncodings = 0;
\t\t\tknownRegions = (
\t\t\t\ten,
\t\t\t\tBase,
\t\t\t\t"zh-Hans",
\t\t\t);
\t\t\tmainGroup = {MAIN_GROUP};
\t\t\tproductRefGroup = {PRODUCTS_GROUP} /* Products */;
\t\t\tprojectDirPath = "";
\t\t\tprojectRoot = "";
\t\t\ttargets = (
\t\t\t\t{TARGET} /* Wobi */,
\t\t\t);
\t\t}};
/* End PBXProject section */"""


def config_section() -> str:
    return f"""/* Begin XCBuildConfiguration section */
\t\t{PROJECT_DEBUG} /* Debug */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
{COMMON_WARNINGS}
{DEBUG_ONLY}
\t\t\t}};
\t\t\tname = Debug;
\t\t}};
\t\t{PROJECT_RELEASE} /* Release */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
{COMMON_WARNINGS}
{RELEASE_ONLY}
\t\t\t}};
\t\t\tname = Release;
\t\t}};
\t\t{TARGET_DEBUG} /* Debug */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
{TARGET_SETTINGS}
\t\t\t}};
\t\t\tname = Debug;
\t\t}};
\t\t{TARGET_RELEASE} /* Release */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
{TARGET_SETTINGS}
\t\t\t}};
\t\t\tname = Release;
\t\t}};
/* End XCBuildConfiguration section */

/* Begin XCConfigurationList section */
\t\t{PROJECT_CONFIG_LIST} /* Build configuration list for PBXProject "Wobi" */ = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = (
\t\t\t\t{PROJECT_DEBUG} /* Debug */,
\t\t\t\t{PROJECT_RELEASE} /* Release */,
\t\t\t);
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};
\t\t{TARGET_CONFIG_LIST} /* Build configuration list for PBXNativeTarget "Wobi" */ = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = (
\t\t\t\t{TARGET_DEBUG} /* Debug */,
\t\t\t\t{TARGET_RELEASE} /* Release */,
\t\t\t);
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};
/* End XCConfigurationList section */"""


def pbxproj() -> str:
    return f"""// !$*UTF8*$!
{{
\tarchiveVersion = 1;
\tclasses = {{
\t}};
\tobjectVersion = 56;
\tobjects = {{

{build_file_section()}

{file_reference_section()}

{group_section()}

{target_section()}

{project_section()}

{phases_section()}

{config_section()}

\t}};
\trootObject = {PROJECT_ID} /* Project object */;
}}
"""


def scheme() -> str:
    reference = (
        f'<BuildableReference BuildableIdentifier = "primary" '
        f'BlueprintIdentifier = "{TARGET}" BuildableName = "Wobi.app" '
        f'BlueprintName = "Wobi" ReferencedContainer = "container:Wobi.xcodeproj">\n'
        f"            </BuildableReference>"
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Scheme LastUpgradeVersion = "1500" version = "1.7">
   <BuildAction parallelizeBuildables = "YES" buildImplicitDependencies = "YES">
      <BuildActionEntries>
         <BuildActionEntry buildForTesting = "YES" buildForRunning = "YES" buildForProfiling = "YES" buildForArchiving = "YES" buildForAnalyzing = "YES">
            {reference}
         </BuildActionEntry>
      </BuildActionEntries>
   </BuildAction>
   <TestAction buildConfiguration = "Debug" selectedDebuggerIdentifier = "Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier = "Xcode.DebuggerFoundation.Launcher.LLDB" shouldUseLaunchSchemeArgsEnv = "YES" shouldAutocreateTestPlan = "YES">
      <Testables>
      </Testables>
   </TestAction>
   <LaunchAction buildConfiguration = "Debug" selectedDebuggerIdentifier = "Xcode.DebuggerFoundation.Debugger.LLDB" selectedLauncherIdentifier = "Xcode.DebuggerFoundation.Launcher.LLDB" launchStyle = "0" useCustomWorkingDirectory = "NO" ignoresPersistentStateOnLaunch = "NO" debugDocumentVersioning = "YES" debugServiceExtension = "internal" allowLocationSimulation = "YES">
      <BuildableProductRunnable runnableDebuggingMode = "0">
         {reference}
      </BuildableProductRunnable>
   </LaunchAction>
   <ProfileAction buildConfiguration = "Release" shouldUseLaunchSchemeArgsEnv = "YES" savedToolIdentifier = "" useCustomWorkingDirectory = "NO" debugDocumentVersioning = "YES">
      <BuildableProductRunnable runnableDebuggingMode = "0">
         {reference}
      </BuildableProductRunnable>
   </ProfileAction>
   <AnalyzeAction buildConfiguration = "Debug"/>
   <ArchiveAction buildConfiguration = "Release" revealArchiveInOrganizer = "YES"/>
</Scheme>
"""


def workspace() -> str:
    return """<?xml version="1.0" encoding="UTF-8"?>
<Workspace
   version = "1.0">
   <FileRef
      location = "self:">
   </FileRef>
</Workspace>
"""


def main() -> None:
    PROJECT.mkdir(parents=True, exist_ok=True)
    scheme_dir = PROJECT / "xcshareddata" / "xcschemes"
    scheme_dir.mkdir(parents=True, exist_ok=True)
    workspace_dir = PROJECT / "project.xcworkspace"
    workspace_dir.mkdir(parents=True, exist_ok=True)

    (PROJECT / "project.pbxproj").write_text(pbxproj(), encoding="utf-8", newline="\n")
    (scheme_dir / "Wobi.xcscheme").write_text(scheme(), encoding="utf-8", newline="\n")
    (workspace_dir / "contents.xcworkspacedata").write_text(
        workspace(), encoding="utf-8", newline="\n"
    )
    print(f"wrote {PROJECT / 'project.pbxproj'}")
    print(f"wrote {scheme_dir / 'Wobi.xcscheme'}")
    print(f"wrote {workspace_dir / 'contents.xcworkspacedata'}")


if __name__ == "__main__":
    main()
