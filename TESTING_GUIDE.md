# Testing Guide for DatabaseProvisioner

This guide explains how to test the new `DatabaseProvisioner` using the provided test scripts.

## Test Scripts Available

### 1. `test_database_provisioner.py` - Comprehensive Test
**Purpose**: Full-featured test script that thoroughly tests the DatabaseProvisioner
**Default Project**: Project 2
**Features**:
- Fetches all project data from database
- Tests project dictionary creation
- Validates project data
- Performs actual provisioning
- Verifies generated files
- Tests startup kit generation
- Provides detailed output and debugging information

**Usage**:
```bash
# Test with default project 2
python test_database_provisioner.py

# Test with custom project ID
python test_database_provisioner.py 3
```

### 2. `quick_test_provisioner.py` - Quick Test
**Purpose**: Simple, fast test to verify basic provisioning functionality
**Default Project**: Project 2
**Features**:
- Basic project validation
- Quick provisioning test
- Simple verification of results
- Minimal output for quick feedback

**Usage**:
```bash
python quick_test_provisioner.py
```

## Prerequisites

1. **Database Setup**: Ensure your database has project 2 (or your test project) with:
   - At least one server
   - At least one client
   - At least one admin (optional but recommended)

2. **Environment**: Make sure you're in the project root directory and have the virtual environment activated:
   ```bash
   source ~/FL/bin/activate
   ```

3. **Dependencies**: Ensure all required packages are installed

## Running the Tests

### Step 1: Activate Virtual Environment
```bash
source ~/FL/bin/activate
```

### Step 2: Run Quick Test (Recommended First)
```bash
python quick_test_provisioner.py
```

This will:
- Check if project 2 exists
- Verify it has required participants
- Run a quick provisioning test
- Clean up automatically

### Step 3: Run Comprehensive Test
```bash
python test_database_provisioner.py
```

This will:
- Show detailed project information
- Test all components of the provisioner
- Generate and verify startup kits
- Provide extensive debugging output

## Expected Output

### Successful Test Output
```
🚀 Quick test of DatabaseProvisioner for project 2
✅ Found project: My Test Project
📊 Participants: 1 servers, 1 clients, 1 admins
🔧 Starting provisioning...
✅ Provisioning successful!
📁 Workspace: /path/to/workspace/project_2
📁 Generated directories: ['FLServer.com', 'site-1', 'admin@nvidia.com']
✅ Server directory: Yes
✅ Client directory: Yes
✅ Admin directory: Yes
🧹 Cleaned up workspace

🎉 Quick test completed successfully!
```

### Error Output
```
❌ Project 2 not found in database
```
or
```
❌ No servers found for project 2
```

## Troubleshooting

### Common Issues

1. **"Project not found"**
   - Check if project 2 exists in your database
   - Use a different project ID: `python test_database_provisioner.py 1`

2. **"No servers found"**
   - Add at least one server to the project in your database
   - Ensure the server has required fields (name, org, ports)

3. **"No clients found"**
   - Add at least one client to the project in your database
   - Ensure the client has required fields (name, org)

4. **"NVFlare not available"**
   - Ensure NVFlare is installed and accessible
   - Check your Python path and virtual environment

5. **"Permission denied"**
   - Ensure you have write permissions in the current directory
   - Check if the workspace directory can be created

### Debug Mode

For more detailed debugging, you can modify the test scripts to:
- Add more print statements
- Check intermediate files
- Verify database connections
- Test individual components

## Customizing Tests

### Testing Different Projects
```bash
# Test project 1
python test_database_provisioner.py 1

# Test project 3
python test_database_provisioner.py 3
```

### Testing with Different Workspace
Modify the test scripts to use a different workspace directory:
```python
provisioner = DatabaseProvisioner(workspace_dir="my_custom_workspace")
```

### Testing Specific Components
You can modify the test scripts to test only specific parts:
- Project dictionary creation
- Validation only
- Provisioning only
- Startup kit generation only

## Integration with Existing Tests

These test scripts complement the existing `test_provisioner.py` by:
- Using the new `DatabaseProvisioner` instead of `NVFlareProvisionerService`
- Following the same database-driven approach
- Providing similar verification capabilities
- Offering both quick and comprehensive testing options

## Next Steps

After successful testing:
1. Integrate the `DatabaseProvisioner` into your application
2. Update your provisioning endpoints to use the new provisioner
3. Test with real project data
4. Monitor performance and error handling
5. Add any customizations needed for your specific use case
