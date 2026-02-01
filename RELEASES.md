# DIZEST Release Notes

This document contains the version history and changelog for DIZEST.

## Version 4.x (Current)

### 4.0.15
> Latest Release

**Enhancements:**
- Added flow status in response at External API

---

### 4.0.14

**Changes:**
- Removed renderer at External API for performance optimization

---

### 4.0.13

**Bug Fixes:**
- Fixed display log bug (whitespace pre-wrap)

---

### 4.0.12

**Bug Fixes:**
- Fixed UI Mode ACL bug

---

### 4.0.11

**Bug Fixes:**
- Fixed App category sort bug
- Fixed Flow instance bug in External API

---

### 4.0.10

**Bug Fixes:**
- Fixed External API UI path bug

---

### 4.0.9

**Enhancements:**
- Added finish event at External API Stream mode

**Bug Fixes:**
- Fixed External API UI bug

---

### 4.0.8

**Bug Fixes:**
- Fixed workflow kernel bug related to ID generation

---

### 4.0.7

**New Features:**
- Added External API UI
- Added Bearer Token authentication for External API

**Bug Fixes:**
- Fixed workflow status bug in core

---

### 4.0.6

**Bug Fixes:**
- Fixed default config bug

---

### 4.0.5

**New Features:**
- Added variable type checking to workflow nodes
- Added `dizest run <workflow_file>` command
- Added External Workflow Running API

---

### 4.0.4

**Enhancements:**
- Updated to LLM Stream mode
- Added ID & password option support at login

---

### 4.0.3

**Bug Fixes:**
- Fixed file browser bug on workflow node file selector

---

### 4.0.2

**Enhancements:**
- Allowed relative library paths when running workflows (sys.path.append)
- Enabled copying of workflow result values
- Added functionality to view and upgrade DIZEST versions per Python environment in settings

**Bug Fixes:**
- Fixed interval disabling issue in Health feature
- Resolved execution order error in workflows (cache issue with previously executed workflows)

---

### 4.0.1

**Bug Fixes:**
- Fixed UI Mode path bug

---

### 4.0.0
> October 6, 2024 - Major Release

**Major Features:**
- Added support for LLM (Large Language Model) integration
- Core updates for better MSA (Microservices Architecture) compatibility

**UI/UX Improvements:**
- Improved workflow UI for better usability (node size adjustment)
- Enhanced usability of UI mode (updated positioning for better node integration)
- Improved Codeflow usability (including scrolling enhancements)
- Updated screen layout and structure

**Technical Details:**
This major version represents a significant architectural upgrade with focus on AI integration and modern service architecture patterns.

---

## Version 3.x

### Version 3.4.15
> August 7, 2022

**Bug Fixes:**
- Fixed version mismatch bug

---

### Version 3.4.14

**Bug Fixes:**
- Resolved UI mode issues

---

### Version 3.4.13

**Major Updates:**
- **Angular Upgrade**: Upgraded UI framework to Angular 18
  - Enhanced performance and development flexibility
  - Improved component architecture
  - Better TypeScript integration

**UI Improvements:**
- Moved App List to the sidebar in workflows
- Improved workflow navigation
- Enhanced overall user experience

**Bug Fixes:**
- Various UI mode bug fixes

---

### Version 3.x Summary
> August 7, 2022

**Highlights:**
- **UI Enhancements**: Multiple bug fixes related to the user interface across all versions
- **Framework Modernization**: Angular 18 upgrade representing a significant update
- **UX Improvements**: Better workflow navigation and layout organization

---

## Version 2.x

### Version 2.2.1

**Updates:**
- Updated to Wiz 1.0
- Enhanced backend configuration management

---

### Version 2.2.0

**New Features:**
- Drag-and-drop input/output ordering in app editor
- CDN configuration support

**Improvements:**
- Significant changes to the app editor interface
- Enhanced app development workflow

---

### Version 2.1.5

**Updates:**
- Kernel configuration updates
- Improved backend stability

---

### Version 2.1.4

**Enhancements:**
- Updated workflow app variable types
- Type system improvements

---

### Version 2.0.8

**Bug Fixes:**
- Workflow stability improvements
- Class-related workflow issue fixes

---

### Version 2.0.7

**Improvements:**
- Socket communication enhancements
- Performance optimizations

---

### Version 2.0.6

**Bug Fixes:**
- General stability improvements

---

### Version 2.0.5

**New Features:**
- Workflow import/export functionality
- Error status display improvements
- Process killing capability on admin dashboard

---

### Version 2.0.0
> May 8, 2022 - Major Release

**Major Features:**
- **Workflow Engine Upgrade**: Complete overhaul of the workflow execution engine
- **App Development API**: Major upgrades to the app development interface
- **Drive Concept**: Introduction of the Drive system for file management
- **UI/UX Overhaul**: Complete redesign of the user interface

**Workflow Management:**
- Enhanced workflow creation and editing
- Improved workflow execution control
- Better error handling and reporting

**Admin Features:**
- Enhanced admin dashboard
- Better process management
- Improved monitoring capabilities

---

### Version 2.x Summary
> May 8, 2022

**Highlights:**
- **Major Engine Upgrades**: Complete workflow engine and API overhaul
- **Enhanced File Management**: Introduction of Drive concept
- **Improved Workflow Tools**: Import/export, better error handling
- **Better Development Experience**: Enhanced app editor with drag-and-drop features

---

## Version 1.x

### Version 1.0.0
> January 18, 2022 - Initial Release

**Initial Features:**
- Visual workflow editor with drag-and-drop interface
- Basic App system for reusable components
- Python-based workflow execution
- Web-based UI
- RESTful API endpoints
- Basic user authentication
- Workflow persistence (.dwp files)

**Core Capabilities:**
- Create and edit workflows visually
- Connect Apps through inputs and outputs
- Execute workflows with real-time logging
- Save and load workflow definitions
- Basic visualization support

**Foundation:**
This release established the core architecture and fundamental concepts that continue to power DIZEST today.

---

## Migration Guides

### Upgrading to 4.x from 3.x

**Breaking Changes:**
- LLM integration requires additional configuration
- Some API endpoints have been restructured for MSA compatibility

**Migration Steps:**
1. Backup your existing workflows
2. Update DIZEST: `pip install dizest --upgrade`
3. Navigate to your project: `cd myproject`
4. Run upgrade command: `dizest upgrade`
5. Review and update any custom integrations
6. Test workflows thoroughly

### Upgrading to 3.x from 2.x

**Breaking Changes:**
- Angular 18 requires modern browser support
- Some UI components have been restructured

**Migration Steps:**
1. Ensure browser compatibility (Chrome 90+, Firefox 88+, Safari 14+)
2. Update DIZEST: `pip install dizest --upgrade`
3. Run upgrade command: `dizest upgrade`
4. Review UI customizations if any

### Upgrading to 2.x from 1.x

**Breaking Changes:**
- Workflow engine API has been significantly changed
- App development API has new structure
- File management now uses Drive concept

**Migration Steps:**
1. **Backup all workflows**: Version 1.x workflows may need manual migration
2. Update DIZEST: `pip install dizest --upgrade`
3. Create new project structure: `dizest install newproject`
4. Manually migrate workflows using the new App development API
5. Update any custom Python code to use new Drive API
6. Test all workflows thoroughly

**API Changes:**
- Old file access methods deprecated in favor of Drive API
- Workflow execution callbacks restructured
- Event system enhanced with new event types

---

## Support

For questions or issues with any version:
- **GitHub Issues**: [Report bugs or request features](https://github.com/season-framework/dizest/issues)
- **Documentation**: [Complete guides](./docs/kr/README.md)
- **Email**: proin@season.co.kr

## License

All versions are released under the MIT License.

Copyright (c) 2021-2026 SEASON CO. LTD.
