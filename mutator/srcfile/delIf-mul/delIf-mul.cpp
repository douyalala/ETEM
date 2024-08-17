//------------------------------------------------------------------------------
// mutate strategy: delete a if stmt
// usage: delIf-mul <path to main.c> --  <position>
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

static llvm::cl::OptionCategory VisitAST_Category("usage: delIf-mul <path to main.c> --  <position>");
static int64_t position = -1;

// By implementing RecursiveASTVisitor, we can specify which AST nodes
// we're interested in by overriding relevant methods.
class MyASTVisitor : public RecursiveASTVisitor<MyASTVisitor> {
public:
  ASTContext *Context=NULL;
  MyASTVisitor(Rewriter &R) : TheRewriter(R) {}

  bool VisitStmt(Stmt *S) {
    if(S->getID(*Context)==position){
      cout<<"mutate here"<<endl;
      TheRewriter.ReplaceText(S->getSourceRange(),"");
      return false;
    }
    return true;
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

  int CopyFile(char *SourceFile,char *NewFile) 
  {  
    ifstream in; 
    ofstream out;  
    in.open(SourceFile,ios::binary);//
    if(in.fail())//
    {     
        cout<<"Error 1: Fail to open the source file."<<endl;    
        in.close();    
        out.close();    
        return 0; 
    }  
    out.open(NewFile,ios::binary);//
    if(out.fail())//
    {     
        cout<<"Error 2: Fail to create the new file."<<endl;    
        out.close();    
        in.close();    
        return 0; 
    }  
    else//
    {     
        out<<in.rdbuf();    
        out.close();    
        in.close();    
        return 1; 
    } 
  }


  void EndSourceFileAction() override {
    SourceManager &SM = TheRewriter.getSourceMgr();
    llvm::errs() << "** EndSourceFileAction for: "
                 << SM.getFileEntryForID(SM.getMainFileID())->getName() << "\n";

    CopyFile("main.c", "mainori.c");
    TheRewriter.overwriteChangedFiles();
    rename("main.c", "mainvar.c");
    rename("mainori.c", "main.c");
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
  position = atol(argv[3]);

  cout<<"-- running: delIf-mul"<<endl;
  cout<<"---- position: "<<position<<endl;

  llvm::Expected<clang::tooling::CommonOptionsParser> OptionsParser = CommonOptionsParser::create(argc, argv, VisitAST_Category);
  ClangTool Tool(OptionsParser->getCompilations(), OptionsParser->getSourcePathList());
  Tool.run(newFrontendActionFactory<MyFrontendAction>().get());

  return 0;
}
