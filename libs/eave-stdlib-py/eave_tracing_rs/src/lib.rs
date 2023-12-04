// use log::info;
use pyo3::{prelude::*, types::PyTuple};

#[pyfunction]
fn eave_tracefunc(frame: &PyAny, event: String, arg: &PyAny) -> PyResult<()> {
    // println!("hello from rust");
    Ok(())
}

/// A Python module implemented in Rust.
#[pymodule]
fn eave_tracing(_py: Python, m: &PyModule) -> PyResult<()> {
    // pyo3_log::init();
    m.add_function(wrap_pyfunction!(eave_tracefunc, m)?)?;
    Ok(())
}
