<h1>specd</h1>

Command-line interface (CLI) for making Swagger 2.0 projects easier to maintain
by breaking the paths and definitions out into discrete folders and files in OpenAPI Specification 2.0 format

<h1>Installing</h1>

Install and update using pip
```bash
$ pip install specd --upgrade
```
<h1>specd Components</h1>

- Structure
  ---
	```bash
	.
	├── definitions
	│   ├── Foo.yaml
	│   └── Bar.yaml
	└── paths
    	├── foo
    	│   └── {fooId}
    	│	├── get.yaml
    	│	└── post.yaml
		├── etc ...
    	└── etc ...
	```
	<h5>Paths</h5>
	The paths and definitions of the specification file get broken out into
	separate directories. The `paths` directory contains OpenAPI specs for every method that was defined in the original 		specification file. In this example, the swagger definition for the API's `GET` method that would be found at example 		URL `hostname.io/foo/{fooId}/`, lives in `paths/foo/{fooId}/get.yaml`
	<h5>Definitions</h5>
	The definitions of the specd are used as models to populate response fields, request body fields, and really anything 		else in the Swagger UI that requires a model of an object
    
- yaml and json Spec Files
  ---
  All specification files are in the OpenAPI Specification 2.0 format. Below are examples of a `path`, `definition`, `.yaml` specification files that correspond with the example directory structure above.
 
 	__`get.yaml` - path__
 	```yaml
 	description: Returns a single pet
 	operationId: get_foo_by_fooId
    produces:
	   - application/json
 	parameters:
  - description: ID of pet to return
    format: int32
    in: path
    name: fooId
    required: true
    type: integer
  responses:
    '200':
      description: successful operation
      schema:
        $ref: '#/definitions/Foo'  #Reference to the Foo model in definitions that is returned on response
    '400':
      description: Invalid bar supplied
    '404':
      description: foo object not found
    tags:
	   - foo
 	```
 
 	__`Foo.yaml` - definition__
 	```yaml
 	properties:
 	  bar:
      $ref: "#/definitions/Bar"
    fooId:
      format: int32
      type: integer
    data_entries:
      items:
        type: string
      type: array
    name:
     type: string
 	title: Foo
 	type: object
 	```
<h1>Core Features</h1>

- Converting a Specification File to a specd: `convert`
  ---
    `convert` takes a swagger specification file as input and an output
    directory as arguments, and creates a specd directory with the following 
    
    <h5>Command Options</h5>
      
    | Command Options         | Description                                         | Default | Values           |  
    |-------------------------|-----------------------------------------------------|---------|------------------|
    | `-f, --format`          | specify the format of the files in the output specd | `yaml`  | `json` or `yaml` |
    
    <h5>Example</h5>
    
    To get the specification file that defines the Swagger Petstore UI at <https://petstore.swagger.io/>, perform a wget to download the specification.json file, and then perform a convert on it
    ```bash
    $ wget "http://petstore.swagger.io/v2/swagger.json" 
    $ specd convert ./swagger.json ~/petstore/
    ```
    By specifying the output directory to be `~/petstore/`, specd will automatically create this directory if it does not already exist, and create a `specs` directory within it that contains a `specd.yaml` file, a `paths` directory, and a `definitions` directory.
    ```bash
    .
    ├── petstore
    │   └── specs
    │       ├── definitions [not opening dir to save space]
    │       │   ├── ApiResponse.yaml
    │       │   ├── Category.yaml
    │       │   ├── Order.yaml
    │       │   ├── Pet.yaml
    │       │   ├── Tag.yaml     
    │       │   └── User.yaml
    │       ├── paths
    │       │   ├── pet
    │       │   │   └── ... [omitting subdirs to save space]
    │       │   ├── store
    │       │   │   └── ... [omitting subdirs to save space]
    │       │   └── user
    │       │       └── ... [omitting subdirs to save space]
    │       └── specd.yaml
    └── swagger.json
    ```
    
    
- Generating a Specification File: `generate`
  ---
    `generate` is the inverse of the `convert` command. It takes a specd directory
    and an output file as arguments, and generates a swagger specification file
    from the path and definition files of the specd directory
    
    <h5>Command Options</h5>
    
   | Command Options       | Description                                                                                        | Default | Values            |  
   |:-------------|:---------------------------------------------------------------------------------------------------|:--------|:------------------|
   | `-c, --case` | specify if operation names in specification file <br> should be converted to `snake_case` or `camelCase` | `snake` | `snake` or `camel`|
    
    <h5>Example</h5> 
     
    Continuing off of the example from the `convert` command, we can create a new specification file for the Swagger Petstore API in yaml format based off of our specd directory
    ```bash
    $ specd generate ~/petstore/specs ~/new_generated_spec.yaml
    $ cd ~
    $ ls
    petstore/	swagger.json	new_generated_spec.yaml
    ```
    
- Running Swagger: `swagger`
  ---
    `swagger` starts a flask app for Swagger UI, allowing you to view and test your API. This command must be run out of your specd directory in order to function properly.   
    
    <h5>Command Options</h5>
    
    | Command Options          | Description                                                                   | Default | Values/Type                   |  
    |:------------------ |:------------------------------------------------------------------------------|:--------|:------------------------------|
    | `-h,`<br> `--host`    | specify the host name of the server you <br>wish to hit with your swagger app. <br> If `None` is given, then specd retrieves a <br>hostname from the `specd.yaml` file within the specd directory| `None`  | Any `str`            |
    | `-n,` <br>`--name`    | specify name of API                                                           | `None`  | Any `str`                     |
    | `-t, --target` | specify the target API endpoints that you wish to be displayed | `None`  | Comma separated list of `str` |

	<h5>Example</h5>
	
    ```bash
    $ cd ~/petstore/specs
    $ specd swagger --name="swagger_petstore"
      * Serving Flask app "specd.app" (lazy loading)
 	  * Environment: swagger
 	  * Debug mode: off
 	  * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    
	```
    By simply doing a `CTRL+click` on the URL you receive from the command line, you can access and test your swagger specd.
<h1>Additional Utility Commands</h1>

-   Comparing Specifications: `diff`
    ---
    `diff` takes two swagger specification files as arguments, and displays path and 
    definition differences between the two
    <h5>Example</h5>
    
    ```bash
    $ specd diff ~/swagger.json ~/new_generated_spec.yaml
    ```
    
-	List Definitions and Paths: `ls`
     ---
     `ls` can be run inside of a specd directory in order to display all definitions and paths for that spec
    
     <h5>Example</h5>
    
     ```bash
     $ cd ~/petstore/specs
     $ specd ls
    
    	Definitions:

			  ApiResponse
			  Category
			  Order
			  Pet
			  Tag
			  User

		  Paths:

		  	/pet/findByStatus: get
		  	/pet/findByTags: get
		  	/pet/{petId}/uploadImage: post
		  	/pet/{petId}: delete, get, post
		  	/pet: post, put
		  	/store/inventory: get
		  	/store/order/{orderId}: delete, get
		  	/store/order: post
		  	/user/createWithArray: post
		  	/user/createWithList: post
		  	/user/login: get
		  	/user/logout: get
		  	/user/{username}: delete, get, put
		  	/user: post
	 ```
	 
- 	Linting Path and Definition Files: `lint`
  	 ---
  	 When a specification swagger file is first broken out into *definition* and *paths* directories using `convert`, the file may have contained fields and types that are not registered with bravado. Although this does not directly affect the API spec's ability to function, logging can become very cluttered, as whenever bravado encounters an unregistered field, it throws a warning message. 
  
  	 Running the `lint` command takes a path to a specd directory as its only argument. When it is executed, `lint` will recursively traverse every single path and definition .json/.yaml file in the specd directory and remove any lines that will cause bravado to throw warnings.
     
     <h5>Example</h5>
     
     ```bash
     $ specd lint ~/petstore/specs
     ```
     
-	Validate Specd Directory: `validate`
	 ---
     `validate` takes no arguments, and will verify if your current working directory is a valid specd directory 
     ```bash
     $ cd ~/petstore/specs
     $ specd
     > Successfully validated.
     ```
