//------------------------------------------------------------------------------
// mutate strategy: replace a loop var (for)
// input: 0, 1(i+1), 2(2*i)
// select positions in main.c that can mutate
// usage: repLoopCond-sel <path to main.c> --  <output dir>
//------------------------------------------------------------------------------
#include <sstream>
#include <string>
#include <iostream>
#include <fstream>
#include <stdio.h>
#include <dirent.h>
#include <memory>
#include <map>
#include <set>
#include <vector>
#include <deque>
#include "clang/AST/AST.h"
#include "clang/AST/ASTConsumer.h"
#include "clang/AST/ASTContext.h"
#include "clang/AST/RecursiveASTVisitor.h"
#include "clang/Frontend/ASTConsumers.h"
#include "clang/Frontend/FrontendActions.h"
#include "clang/Frontend/CompilerInstance.h"
#include "clang/Tooling/CommonOptionsParser.h"
#include "clang/Tooling/Tooling.h"
#include "clang/Rewrite/Core/Rewriter.h"
#include "llvm/Support/raw_ostream.h"
#include "clang/Lex/Lexer.h"
using namespace std;
using namespace clang;
using namespace clang::driver;
using namespace clang::tooling;

static llvm::cl::OptionCategory VisitAST_Category("usage: repLoopCond-sel <path to main.c> --  <output dir>");
static string output_dir = "";
static ofstream out;
static vector<int64_t> res_pos;

// By implementing RecursiveASTVisitor, we can specify which AST nodes
// we're interested in by overriding relevant methods.
class MyASTVisitor : public RecursiveASTVisitor<MyASTVisitor> {
public:
  ASTContext *Context=NULL;
  MyASTVisitor(Rewriter &R) : TheRewriter(R) {}

  bool VisitStmt(Stmt *S) {
    if (isa<ForStmt>(S)){
      ForStmt* ForS=cast<ForStmt>(S);
      Stmt* Init=ForS->getInit();
      cerr<<Init->getStmtClassName()<<endl;

      bool find=false;

      if (Init && isa<DeclStmt>(Init)) {
          DeclStmt *DeclStmtS = cast<DeclStmt>(Init);
          for (DeclStmt::const_decl_iterator it = DeclStmtS->decl_begin(); it != DeclStmtS->decl_end(); ++it) {
              if (isa<VarDecl>(*it)) {
                  VarDecl *Var = cast<VarDecl>(*it);
                  std::string VarName = Var->getNameAsString();
                  if (!VarName.empty()) {
                    find=true;
                    cerr << "Variable in for loop init: " << VarName << "\n";
                  }
              }
          }
      }

      if(find){
        res_pos.push_back(S->getID(*Context));
      }
    }

    return true;
  }

  bool TraverseStmt(Stmt *S) {
    bool result = 0;
    if(Context==NULL){
      llvm::errs() <<"Error: Context is NULL" << "\n";
      return 0;
    }

    result = RecursiveASTVisitor::TraverseStmt(S);

    return result;
  }

private:
  Rewriter &TheRewriter;
};

// Implementation of the ASTConsumer interface for reading an AST produced
// by the Clang parser.
class MyASTConsumer : public ASTConsumer {
public:
  MyASTConsumer(Rewriter &R) : Visitor(R) {}

  void HandleTranslationUnit(ASTContext &Context) override  {
    /* we can use ASTContext to get the TranslationUnitDecl, which is
       a single Decl that collectively represents the entire source file */
    Visitor.Context=&Context;
    Visitor.TraverseDecl(Context.getTranslationUnitDecl());
  }

private:
  MyASTVisitor Visitor;
};

// For each source file provided to the tool, a new FrontendAction is created.
class MyFrontendAction : public ASTFrontendAction {
public:
  MyFrontendAction() {}

  void EndSourceFileAction() override {
    SourceManager &SM = TheRewriter.getSourceMgr();
    llvm::errs() << "** EndSourceFileAction for: "
                 << SM.getFileEntryForID(SM.getMainFileID())->getName() << "\n";
  }

  std::unique_ptr<ASTConsumer> CreateASTConsumer(CompilerInstance &CI,
                                                 StringRef file) override {
    llvm::errs() << "** Creating AST consumer for: " << file << "\n";
    TheRewriter.setSourceMgr(CI.getSourceManager(), CI.getLangOpts());
    return make_unique<MyASTConsumer>(TheRewriter);
  }

private:
  Rewriter TheRewriter;
};

int main(int argc, const char **argv) {
  output_dir = argv[3];

  cout<<"-- running: repLoopCond-sel"<<endl;
  cout<<"---- output_dir: "<<output_dir<<endl;

  llvm::Expected<clang::tooling::CommonOptionsParser> OptionsParser = CommonOptionsParser::create(argc, argv, VisitAST_Category);
  ClangTool Tool(OptionsParser->getCompilations(), OptionsParser->getSourcePathList());
  Tool.run(newFrontendActionFactory<MyFrontendAction>().get());

  out.open(output_dir,ios::trunc);
  if(out.fail()){     
    llvm::errs() <<"Error: Fail to open the out file." << "\n";
    out.close();
    return 0; 
  }
  for(long unsigned int i=0;i<res_pos.size();i++){
    out<<res_pos[i]<<endl;
  }

  return 0;
}
