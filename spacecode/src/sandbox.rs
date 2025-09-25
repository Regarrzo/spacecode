use wasmtime;
use std;

pub trait Sandbox {
    /// Initialise or reset the sandbox
    fn init(&mut self);
    /// Send `message` to the sandbox
    fn send(&mut self, message: String);
    /// Ask the sandbox for a message to read, then return it.
    fn read(&mut self) -> String;
}

pub struct Wasm<T> {
    engine: wasmtime::Engine,
    module: wasmtime::Module,
    instance: wasmtime::Instance,
    linker: wasmtime::Linker<T>,
}

impl<T> Wasm<T> {
    pub fn new(module_path: &str) -> Result<Wasm<T>, std::io::Error> {
        let engine = wasmtime::Engine::default();
        let component = wasmtime::component::Component::from_file(&engine, module_path);
        let instance = wasmtime::Instance
        
        

    }

}