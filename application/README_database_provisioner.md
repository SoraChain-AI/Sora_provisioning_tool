# Database Provisioner

A new provisioning script that creates NVFlare project configurations directly from database data, following the same pattern as NVFlare's `provision.py` file.

## Overview

The `DatabaseProvisioner` class provides a clean interface to provision NVFlare projects using data stored in the database, without needing to create custom YAML files or manage complex provisioning contexts manually.

## Key Features

- **Database-driven**: Creates project configurations directly from database models
- **NVFlare-compatible**: Uses the same provisioner API as NVFlare's official tools
- **Simple interface**: Minimal setup required - just provide project ID
- **Automatic validation**: Validates project data before provisioning
- **Startup kit generation**: Generates startup kits for servers, clients, and admins
- **Error handling**: Comprehensive error handling and logging

## Architecture

The provisioner follows the same pattern as NVFlare's `provision.py`:

1. **Data Extraction**: Retrieves project, server, client, and admin data from database
2. **Project Dictionary Creation**: Converts database models to NVFlare-compatible dictionary format
3. **Project Object Preparation**: Creates `ProvProject` object using `participant_from_dict()`
4. **Provisioner Setup**: Uses `prepare_builders()` and `prepare_packager()` from NVFlare
5. **Provisioning**: Calls `provisioner.provision()` to generate all configuration files
6. **Result Extraction**: Copies generated files to final workspace

## Usage

### Basic Usage

```python
from database_provisioner import DatabaseProvisioner

# Create provisioner instance
provisioner = DatabaseProvisioner(workspace_dir="my_workspace")

# Provision a project
result = provisioner.provision_project(project_id=1, force_reprovision=False)

if result:
    print(f"Project provisioned successfully: {result}")
else:
    print("Provisioning failed")
```

### Using Convenience Function

```python
from database_provisioner import provision_project_from_database

# One-line provisioning
result = provision_project_from_database(
    project_id=1, 
    workspace_dir="my_workspace", 
    force_reprovision=False
)
```

### Command Line Usage

```bash
# Basic usage
python database_provisioner.py 1

# With custom workspace
python database_provisioner.py 1 my_workspace

# Force reprovision
python database_provisioner.py 1 my_workspace true
```

### Generating Startup Kits

```python
# Generate startup kit for server
kit_buffer, filename = provisioner.generate_startup_kit(project_id=1, item_type='server')

# Generate startup kit for specific client
kit_buffer, filename = provisioner.generate_startup_kit(
    project_id=1, 
    item_type='client', 
    item_id=5
)

# Generate all startup kits
all_kits = provisioner.generate_startup_kit(project_id=1, item_type='all')
```

## Database Requirements

The provisioner expects the following database models:

### Project Model
- `id`: Project ID
- `name`: Project name
- `short_name`: Short name (optional)
- `description`: Project description
- `project_props`: JSON string with additional properties (optional)

### Server Model
- `id`: Server ID
- `project_id`: Associated project ID
- `name`: Server name
- `org`: Organization name
- `fed_learn_port`: Federated learning port (default: 8002)
- `admin_port`: Admin port (default: 8003)
- `connection_security`: Connection security type (default: 'mtls')
- `props`: JSON string with additional properties (optional)

### Client Model
- `id`: Client ID
- `project_id`: Associated project ID
- `name`: Client name
- `org`: Organization name
- `capacity`: JSON string with capacity configuration (optional)
- `props`: JSON string with additional properties (optional)

### Admin Model
- `id`: Admin ID
- `project_id`: Associated project ID
- `email`: Admin email address
- `org`: Organization name
- `role`: Admin role (default: 'project_admin')
- `props`: JSON string with additional properties (optional)

## Configuration

### Project Properties

Additional project-level properties can be stored in the `project_props` field as JSON:

```json
{
    "scheme": "agrpc",
    "overseer_agent": {
        "path": "nvflare.ha.dummy_overseer_agent.DummyOverseerAgent",
        "overseer_exists": false,
        "args": {
            "sp_end_point": "server:8002:8003"
        }
    }
}
```

### Server Properties

Server-specific properties can be stored in the `props` field:

```json
{
    "connection_security": "mtls",
    "fed_learn_port": 8002,
    "admin_port": 8003,
    "scheme": "agrpc"
}
```

### Client Properties

Client-specific properties including capacity:

```json
{
    "capacity": {
        "num_of_gpus": 4,
        "mem_per_gpu_in_GiB": 16
    }
}
```

## Error Handling

The provisioner includes comprehensive error handling:

- **Validation Errors**: Checks for required fields and valid data
- **Database Errors**: Handles missing projects or participants
- **Provisioning Errors**: Catches and reports NVFlare provisioning failures
- **File System Errors**: Handles workspace creation and file operations

## Comparison with Existing Provisioners

| Feature | DatabaseProvisioner | nvflare_provisioner.py | provisioning.py |
|---------|-------------------|----------------------|-----------------|
| Data Source | Database models | Database models | YAML files |
| NVFlare Integration | Direct API | Direct API | CLI + API |
| Complexity | Low | High | Medium |
| Customization | Database-driven | Manual context | YAML-driven |
| Error Handling | Comprehensive | Basic | Basic |
| Startup Kits | Built-in | Built-in | Manual |

## Dependencies

- NVFlare (for provisioner API)
- SQLAlchemy (for database models)
- Python 3.7+

## Examples

See `example_usage.py` for complete usage examples.

## Troubleshooting

### Common Issues

1. **"Project not found"**: Ensure the project exists in the database
2. **"No servers configured"**: Add at least one server to the project
3. **"No clients configured"**: Add at least one client to the project
4. **"NVFlare not available"**: Install NVFlare or check import paths

### Debug Mode

Enable debug logging by setting environment variables:

```bash
export NVFLARE_DEBUG=1
export PYTHONPATH=/path/to/nvflare:$PYTHONPATH
```

## Future Enhancements

- Support for additional participant types
- Custom builder configurations
- Advanced validation rules
- Batch provisioning support
- Integration with external configuration systems
