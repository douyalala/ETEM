set(LLVM_LINK_COMPONENTS support)

add_clang_executable(repIntConstant-sel
  repIntConstant-sel.cpp
  )
target_link_libraries(repIntConstant-sel
  PRIVATE
  clangAST
  clangASTMatchers
  clangBasic
  clangFrontend
  clangSerialization
  clangTooling
  clangDriver
  clangRewrite
  clangRewriteFrontend
  clangStaticAnalyzerFrontend
  clangToolingSyntax
  )