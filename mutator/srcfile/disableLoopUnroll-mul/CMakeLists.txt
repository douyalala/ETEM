set(LLVM_LINK_COMPONENTS support)

add_clang_executable(disableLoopUnroll-mul
  disableLoopUnroll-mul.cpp
  )
target_link_libraries(disableLoopUnroll-mul
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