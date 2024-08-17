set(LLVM_LINK_COMPONENTS support)

add_clang_executable(dupStmt-mul
  dupStmt-mul.cpp
  )
target_link_libraries(dupStmt-mul
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